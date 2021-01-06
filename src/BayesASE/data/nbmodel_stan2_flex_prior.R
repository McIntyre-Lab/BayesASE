#Extension of the Poisson-Gamma (PG) model with both.
#Instead of assuming a poisson sampling model
#It considers a Negative Binomial model
#See model_extension_withboth9.pdf section for model specification
#This model/program was started July 2019
#It is the stan version of simul_NBmodel_WITHBOTH8_gammaalphadeltainboth_taugamma1.R
#That was used in the published paper
#The correction bias for counts in Line1,q1, can be different from
#the correction bias for counts in Line2
#The mean structure is
#                         Tester           Line 1                       both
#Line 1(mated)            q11*(1/alpha)beta_i       q12*betai*alpha              tau[(1-q11)/alpha+(1-q12)alpha]betai
#Line 2(virgin)           q21*(1/delta)beta_igamma  q22*betai*delta*gamma        tau[(1-q11)/delta+(1-q12)*delta]betai*gamma
#It is required that q11+q12+q13=1  (notice that q13 is in the model implicitely)
rm(list=ls())

library("rstan")
library("here")
rstan_options(auto_write = FALSE)

gam.mles.data = function(x){
  # CALCULATION OF THE MLES for gamma  GIVEN THE SAMPLE
    n = length(x)
  xb = mean(x)
  xd = mean(log(x))
  s = log(xb)-xd
  a0 = (3.0-s+sqrt((s-3.0)^2+24.0*s))/12.0/s
  l = 1
  repeat{
    ans = (log(a0)-digamma(a0)-s)
    a1 = a0-ans/(1.0/a0-trigamma(a0))
    if(abs(ans) <= 1.0e-7 | l >= 30){break}
    a0 = a1
    l = l+1}
  ah = a1; bh = xb/a1
  return(c(ah,bh))
}

#Computing prior hyperparameters for beta, the size effect
prior_empBayes_forbeta=function(xs,ys,zs){
  #Function to compute the hyperparameters of the gamma distribution for 
  #beta_1,...beta_K~beta(a_beta,b_beta) with b_beta~gamma(a_b_beta,b_b_beta)
  bbeta_est=(xs+ys+zs)/2
  bbeta_est[which(bbeta_est==0)]=0.1
  tem=gam.mles.data(bbeta_est) #MLE of the gamma function but it is parameterized so that E(x)=ab if x~gamma(a,b)
  tem[1]=min(max(tem[1],10^(-3)),10^5)  
  tem[2]=min(max(tem[2],10^(-3)),10^5)  #Our gamma parameterization is E(x)=a/b
  a_beta=tem[1]
  a_b_beta=2*tem[2]^(-1)#
  b_b_beta=2 
  return(list(a_beta=a_beta,a_b_beta=a_b_beta,b_b_beta=b_b_beta))
}

# Get command line args with file names for processing

# Import NB Functions
args = commandArgs(trailingOnly=TRUE)

#AMM commmented out following line in 04fm version
#args<-c("/blue/mcintyre/share/BASE_mclab/galaxy/bayesian_in/bayesian_input_W55_M_V.csv","/blue/mcintyre/share/BASE_mclab/galaxy/bayesian_in/test_W55_out.csv",2,".")
#args<-c("/blue/mcintyre/share/BASE_mclab/galaxy/bayesian_in/adj_head_bayesian_input_W55_M.csv","/blue/mcintyre/share/BASE_mclab/galaxy/bayesian_in/test_W55_out.csv",1,".")

# path to environmentalmodel2.stan
stanScript <- args[1]
cat("Stan script: ", stanScript, "\n")
inputFile <- args[2]
cat("Input File", inputFile,"\n")
outputFile <- args[3]
cat("Output File", outputFile, "\n")
nconditions<-as.numeric(args[4])
cat("Number of conditions:",nconditions,"\n")
workdir<-args[5]
cat("Working directory:", workdir,"\n")
setwd(workdir)
nSimulations <- args[6]
nBurnin <- args[7]
# Set number of simulations and burnin. If not set, we have defult to 10^5 iterations and 10^4
# burnin
ifelse(is.na(nSimulations),nsim<-10^5,nsim<-as.numeric(nSimulations))
ifelse(is.na(nBurnin),nburnin<-10^4,nburnin<-as.numeric(nBurnin))
cat("Running with",nburnin,"warmup rounds and",nsim,"iterations\n")

#########################
# Generalize the number of conditions
#########################

seqcond<-paste("c",seq(1,nconditions),sep="")
fornames1=seqcond #Neutral prefix for output names
fornames2=c("sampleprop","theta","q025","q975","Bayes_evidence","AI_decision")
fornames=paste(paste(rep(fornames1,each=length(fornames2)),fornames2,sep="_"),collapse=",")
#The three possible alignment states: better to tester (G1?), better to line (G2?), equally good (both).
#alnto<-c("g1","g2","Both")
counttester<-paste("counts_",seqcond,"_g1",sep="")
countline<-paste("counts_",seqcond,"_g2",sep="")
countboth<-paste("counts_",seqcond,"_both",sep="")
countheader<-paste(counttester,countline,countboth,sep=",",collapse=",")
priorstester<-paste("prior_",seqcond,"_g1",sep="")
priorsline<-paste("prior_",seqcond,"_g2",sep="")
allpriors<-sort(c(priorstester,priorsline))
seqreps<-paste(seqcond,"_num_reps",sep="")
firstheaders=paste(c("comparison","FEATURE_ID",
                     seqreps,
                     countheader,
                      allpriors, 
                      "H3_independence_Bayes_evidence"),
                      collapse=",")

alpha_post_names<-paste(paste("alpha",seq(1,nconditions),"_postmean",sep=""),collapse=",")
cat("alpha names are:",alpha_post_names,"\n")
headers_out=paste(firstheaders,fornames,alpha_post_names,"flaganalyze",sep=",")
cat(headers_out,file=outputFile,append=FALSE,sep="\n")

# Make Connection to input
con = file(inputFile, "r")
newline=readLines(con,n=1) #moving the pointer away from the headers
headers_in=strsplit(newline,split=",")[[1]]

# Begin Processing
print(paste("reading input file ", inputFile))
print(paste("saving results in ", outputFile))

while(length(newline) != 0 ){
    flaganalyze<-0
    while(as.numeric(flaganalyze)==0){
    newline<-readLines(con,n=1);if(length(newline) == 0){break};    
    mydata<-as.vector(strsplit(newline,split=",")[[1]])
    #flaganalzye is the product of all the flags. If just one is zero the result is zero.    
    activeflag<-paste(seqcond,"flag_analyze",sep="_")
    cat("activeflag",activeflag,"\n")
    xactiveflag<-rep(NA,length(activeflag))


    names(mydata)=headers_in[1:length(mydata)]
        # print(paste("length mydata",length(mydata)))
        # print(paste("names mydata",names(mydata)))

    cat("Starting names checking\n")
    #Here we check if column names satisfy the rules
    if(sum(names(mydata)%in%allpriors)!=length(allpriors)) stop("Specified column names for priors do not match expectations. At least the following prior columns must be present: ",paste(allpriors,collapse=" "))
    if(sum(names(mydata)%in%seqreps)!=length(seqreps)) stop("Specified column names for replicate number do not match expectations. At least the following replicate number columns must be present: ",paste(seqreps,collapse=" "))
    if(sum(names(mydata)%in%activeflag)!=length(activeflag)) stop("Specified column names for activeflag do not match expectations. At least the following activeflag columns must be present: ",paste(activeflag,collapse=" "))
    #if(sum(names(mydata)%in%counttester)!=length(counttester)) stop("Specified column names for read counts on haplotype 1 do not match expectations. At least the following haplotype 1 columns must be present: ",paste(counttester,collapse=" "))
    if(length(grep(counttester[1],names(mydata)))<1) stop("Specified column names for read counts on haplotype 1 do not match expectations. At least the following haplotype 1 columns must be present: ",paste(counttester,collapse=" "))
    if(length(grep(countline[1],names(mydata)))<1) stop("Specified column names for read counts on haplotype 2 do not match expectations. At least the following haplotype 2 columns must be present: ",paste(countline,collapse=" "))
    if(length(grep(countboth[1],names(mydata)))<1) stop("Specified column names for unassigned read counts do not match expectations. At least the following unassigned reads counts columns must be present: ",paste(countboth,collapse=" "))

    #cat("Names mydata",names(mydata),"\n")
    for(myact in 1:length(activeflag))
    {
        xactiveflag[myact]<-as.numeric(mydata[which(names(mydata) == activeflag[myact])])
    }

    flaganalyze=prod(xactiveflag);
    if(is.na(flaganalyze)) flaganalyze=0    
    #If flaganalyze==0 we print a line full of NAs.
    if(flaganalyze==0) 
    {
    out=paste(
      paste(rev(mydata)[1],mydata["FEATURE_ID"],sep=","),
      paste(rep(NA,nconditions),sep=",",collapse=","),      #seqI is a vector containing the number of replicates for each condition
#      paste(apply(totalcounts,2,paste,collapse=","),collapse=","),
      paste(rep(NA,3*nconditions),collapse=","),
        paste(rep(NA,2),collapse=","),
        paste(rep(NA,2),collapse=","),
        paste(rep(NA,6*nconditions),collapse=","),
        paste(rep(NA,nconditions),collapse=","),
#this zero is for the flaganalyze condition,
        0,sep=","
      )
    cat(out,file=outputFile,append=TRUE,sep="\n")    
    next
    }
    
    #cat(flaganalyze,"\n")    
    }
  if(length(newline) == 0){break}
    print("----------------------")
    print(paste("comparison:",rev(mydata)[1]))
    print(paste("FEATURE_ID",mydata["FEATURE_ID"]))
    #Inizialize vectors, then loop for the required length and go.        
    cat("Total conditions:",length(seqcond),"\n")
    seqI<-rep(NA,length(seqcond))    
    # xTshort<-paste(gsub("counts_","",counttester),"_total_rep",sep="")
    # xLshort<-paste(gsub("counts_","",countline),"_total_rep",sep="")
    # xBshort<-paste(gsub("counts_","",countboth),"_total_rep",sep="")
    xTshort<-paste(counttester,"_total_rep",sep="")
    xLshort<-paste(countline,"_total_rep",sep="")
    xBshort<-paste(countboth,"_total_rep",sep="")
    cat("Reading conditions\n")
    #Crazy loop to read columns of an arbitrary number of conditions with an arbitrary number of replicates.
    #Strangely enough, it works!
    for(ncond in 1:length(seqcond))
    {
        cat("seqreps[ncond]:",seqreps[ncond],"\n")
        cat("mydata[seqreps[ncond]]:",seqreps[ncond],"\n")
        #seqI is a vector that for each condition reports the number of replicates        
        seqI[ncond]<-as.numeric(mydata[seqreps[ncond]]) #Number of replicates ofr each condition
        if(ncond==1)
        {        
            xT<-paste(xTshort[ncond],seq(1,seqI[ncond]),sep="")
            xL<-paste(xLshort[ncond],seq(1,seqI[ncond]),sep="")
            xB<-paste(xBshort[ncond],seq(1,seqI[ncond]),sep="")
        }else{
            xT<-c(xT,paste(xTshort[ncond],seq(1,seqI[ncond]),sep=""))
            xL<-c(xL,paste(xLshort[ncond],seq(1,seqI[ncond]),sep=""))
            xB<-c(xB,paste(xBshort[ncond],seq(1,seqI[ncond]),sep=""))
        }        
    }
    cat("Read conditions\n")
    # cat("mydata are:",mydata,"\n")
    # cat("names mydata are:",names(mydata),"\n")
    cat("xT are:",xT,"\n")
    cat("mydata[xT] are:",mydata[xT],"\n")
    xs = as.numeric(mydata[xT])#Vector of reads assigned to "tester" allele
    names(xs)<-unlist(lapply(strsplit(xL,"_"),"[",1))
    cat("xs are",xs,"\n")
    cat("names (xs) are", names(xs),"\n")
    ys = as.numeric(mydata[xL])    #Vector of reads assigned to "line" allele
    names(ys)<-unlist(lapply(strsplit(xL,"_"),"[",1))
    zs=    as.numeric(mydata[xB])    #Vector of reads assigned to both alleles
    names(zs)<-unlist(lapply(strsplit(xL,"_"),"[",1))


#    q_= matrix(c(as.numeric(mydata["prior_c1_g1"]),as.numeric(mydata["prior_c1_g2"]),as.numeric(mydata["prior_c2_g1"]),as.numeric(mydata["prior_c2_g2"])) ,nrow=2, byrow=TRUE)  #Bias correction hyperparameter expected percentage of counts aligning to line when no AI
    q_= matrix(c(as.numeric(mydata[allpriors])) ,nrow=2, byrow=TRUE)  #Bias correction hyperparameter expected percentage of counts aligning to line when no AI
        
         cat("q_ before adjustment is:",q_,"\n")
    q_[q_==0]<-0.001+q_[q_==0]
    cat("q_ after adjustment is:",q_,"\n")
    #Checking that I have not a vector of all zeros
      #If so, i will add 1 to one of the entries with zeros
      #(this messes with the convergence) 
        
    for(ncond in 1:length(seqcond))
    {
    if(sum(xs[names(xs)==seqcond[ncond]]+ys[names(ys)==seqcond[ncond]]+zs[names(zs)==seqcond[ncond]])==0) zs[names(zs)==seqcond[ncond]]<-1
    if(sum(zs[names(zs)==seqcond[ncond]])==0) zs[names(zs)==seqcond[ncond]][which.max(xs[names(xs)==seqcond[ncond]]+ys[names(ys)==seqcond[ncond]])]<-1
    if(sum(xs[names(xs)==seqcond[ncond]])==0) xs[names(xs)==seqcond[ncond]][which.max(zs[names(zs)==seqcond[ncond]])]<-1
    if(sum(ys[names(ys)==seqcond[ncond]])==0) ys[names(ys)==seqcond[ncond]][which.max(zs[names(zs)==seqcond[ncond]])]<-1
    }
      
    cat("Assigning beta\n")  
      hyper_beta=prior_empBayes_forbeta(xs,ys,zs)
      #Making the data ready for stan
      datastan=list(
        K=sum(seqI),                 #Total number of bioresps
        n_environment=nconditions,         #Number of environments. So far 2 mated and virgin
        xenv=rep(seq(1,length(seqI)),seqI),       #Environment index mated or virgin
        xs=as.vector(xs),
        ys=as.vector(ys),
        zs=as.vector(zs),
        r=q_,               #matrix of systematic bias corrections

        
        a_beta=hyper_beta$a_beta,               #beta_1,...beta_K~gamma(a_beta,b_beta)
        a_b_beta=hyper_beta$a_b_beta,           #b_beta~gamma(a_b_beta,b_b_beta)
        b_b_beta=hyper_beta$b_b_beta,
        a_overdispersion=2.01,#1,
        b_overdispersion=0.05#100,#phi is apriori small, if inverse gamma is used prior mean b_phi/(a_phi-1)           
      )
    cat("datastan is")  
    print(datastan)

    starting_values=function(){
      out=
        with(datastan,list(overdispersion=0.01,bbeta=xs+ys+zs,
               alpha=rep(1.0,n_environment)))
    return(out)  
      }

    totalcounts=
    rbind(
    xs=tapply(datastan$xs,FUN=sum,INDEX=datastan$xenv),
    ys=tapply(datastan$ys,FUN=sum,INDEX=datastan$xenv),
    zs=tapply(datastan$zs,FUN=sum,INDEX=datastan$xenv)
    )
  
    #if(mydata["FEATURE_ID"]=="S21597_SI") browser()
    #cat(xs,"\n")  
         if(sum(xs+ys)>=1 && sum((q_-q_^2)!=0)>0){
        cat("Analysis starting for FEATURE_ID",mydata["FEATURE_ID"],"\n")

#set.seed(123)
    fit1 <- stan(
      file =  stanScript,# Stan program
      data = datastan,    # named list of data
      chains = 1,             # number of Markov chains
      warmup = nburnin,          # number of warmup iterations per chain
      iter =   nsim,            # total number of iterations per chain
      refresh = 10^3,             # no progress shown
      init="starting_values",
      pars=c("alpha","theta") 
    )
    

    theta<-extract(fit1,pars="theta")$theta #Estimated proportion of reads aligning to tester in mated after adjusting for systematic bias
    alpha<-extract(fit1,pars=c("alpha"))$alpha
    # sigma_alpha=extract(fit1,pars=c("sigma_alpha"))$sigma_alpha
    Stanresults=matrix(NA,nrow=nconditions,ncol=4)
    Bayes_AI_pvalue<-rep(NA,nconditions)
    for(mystan in 1:nrow(Stanresults))
    {
    theta1<-theta[,mystan]
    alpha1<-alpha[,mystan]
    Stanresults[mystan,]<-c(mean(theta1),quantile(theta1,c(0.025,0.975)),
              2*min(mean(mean(theta1>1/2),mean(theta1<1/2)) ))
    Bayes_AI_pvalue[mystan]<-2*min(c(mean(alpha1>1),mean(alpha1<1)))
    }
    colnames(Stanresults)=c("theta","q_025","q_975","AIbayesian-pva")
    cat("Stanresults",Stanresults,"\n")
    
    Stanresults[,"AIbayesian-pva"]
    
    
    # sigma_alpha_out=c(mean(sigma_alpha),quantile(sigma_alpha,c(0.5,0.95)))
        #paste(c(totalcounts[,1],totalcounts[,2],totalcounts[,3]),collapse=","),

        for(repcond in 1:nconditions)
        {
            theta1<-theta[,repcond]
            #For each condition write the proportion of xs over xs+ys
            smallStanres<-paste(round(totalcounts[row.names(totalcounts)=="xs",repcond]/(totalcounts[row.names(totalcounts)=="xs",repcond]+totalcounts[row.names(totalcounts)=="ys",repcond]),4),
            round(mean(theta1),4),
            paste(round(quantile(theta1,c(0.025,0.975)),4),collapse=","),
            round(Bayes_AI_pvalue[repcond],4),
            ifelse(Bayes_AI_pvalue[repcond]<0.05,1,0),sep=",")
            if(repcond==1) fullStanres<-smallStanres else fullStanres<-paste(fullStanres,smallStanres,sep=",",collapse=",")
        }
    alpha1greateralpha2<-NA
    #alpha1greateralpha2 is the bayesian independence test. Only meaningful for two conditions 
    if(nconditions==2) 
    {
    alpha1greateralpha2<-round(min(mean(alpha[,1]>alpha[,2]),mean(alpha[,1]<alpha[,2]))*2,4)
    }
    out=paste(
      paste(rev(mydata)[1],mydata["FEATURE_ID"],
      paste(seqI,sep=",",collapse=","),      #seqI is a vector containing the number of replicates for each condition
      sep=","),
      paste(apply(totalcounts,2,paste,collapse=","),collapse=","),
        paste(apply(datastan$r,1,paste,collapse=","),collapse=","), #write what was formerly called q_ (bias) ALREADY SET TO READ ARBITRARY NUMBER OF CONDITIONS 
        #round(res$independencetest$Chisqpvalue,4),
        #This would be the independence test... We temporarily disregard it when dealing with more than 2 conditions
        alpha1greateralpha2 ,
        fullStanres,
        paste(round(apply(alpha,2,mean),4),collapse=","),1,
        #paste(round(sigma_alpha_out,6),collapse=","),
      sep=",")
    cat("alpha is:",round(apply(alpha,2,mean),4),"\n")
    }else{
      #If all the counts are zero I fill it with NaN
      #browser()
      out=paste(
      paste(rev(mydata)[1],mydata["FEATURE_ID"],
      paste(seqI,sep=",",collapse=","),      #seqI is a vector containing the number of replicates for each condition
      sep=","),
#      paste(apply(totalcounts,2,paste,collapse=","),collapse=","),
      paste(apply(totalcounts,2,paste,collapse=","),collapse=","),
        paste(apply(datastan$r,1,paste,collapse=","),collapse=","),
        paste(rep(NA,2),collapse=","),
        paste(rep(NA,6*nconditions),collapse=","),
        paste(rep(NA,nconditions),collapse=","),
        paste(rep(NA,3),collapse=","),1,sep=","
      )
        }
    #If one wants to see the results in a very long vector
    #outmatrix=cbind(unlist(strsplit(headers_out, ",")),unlist(strsplit(out, ",")))
    #sum(as.numeric(outmatrix[52:55,2]))
    cat(out,"\n")
    cat(out,file=outputFile,append=TRUE,sep="\n")
    }
close(con)
