install.packages("UsingR")
install.packages("R.utils")

source("https://bioconductor.org/biocLite.R")
biocLite("affy")
biocLite("affydata")

library(UsingR)
library(affy)
library(affydata)
library(R.utils)

.libPaths(c("/Users/Kalapala/Desktop/StudyingGeneExp", .libPaths()))
setwd("/Users/Kalapala/Desktop/StudyingGeneExp/")

#Unzip contents of tar file 
#NORMALIZATION USING RMA
Data <- ReadAffy(celfile.path="/Users/Kalapala/Desktop/StudyingGeneExp/", compress=TRUE)
eset <- rma(Data, normalize=TRUE)
normalizedExpr <- exprs(eset)
head(normalizedExpr)
write.exprs(eset, file="ProjectData.txt")

#GETTING TOP VARIANT GENES
geneExpr = read.table("ProjectData.txt")
dim(geneExpr)
#Working with a few top variant genes
newGeneExpr = geneExpr[, 1:12]
save(newGeneExpr, file = "ProjectData2.txt")
load("ProjectData2.txt")
nGene <- nrow(newGeneExpr)
geneVar <- rep(0, nGene)
for(i in 1:nGene){
  geneVar[i] <- var(unlist(geneExpr[i,]))
}

summary(geneVar)

cutoff <- quantile(geneVar, 1-200/nGene)
Top200 <- newGeneExpr[geneVar>cutoff,]
colnames(Top200) <- c(paste("WhiteMatterControl", 1:6, sep = ""), paste("WhiteMatterHIVInfected", 1:6, sep=""))
d <- as.matrix(Top200)

#CONSTRUCTING HEATMAP FOR DATA

heatmap(d)
dev.off()

#DETECTION OF DIFFERENTIALLY EXPRESSED GENES
#Calculating P values
colnames(newGeneExpr) <- c(paste("WhiteMatterControl", 1:6, sep = ""), paste("WhiteMatterHIVInfected", 1:6, sep=""))
C1 <- which(colnames(newGeneExpr) %in% paste("WhiteMatterControl", 1:6, sep =""))
C2 <- which(!(colnames(newGeneExpr) %in% paste("WhiteMatterControl", 1:6, sep = "")))
genePvalues <- apply(newGeneExpr, 1, function(x) t.test(x[C1], x[C2])$p.value)

#Adjusting P values based on BH procedure
AdjustedPvalues <- p.adjust(genePvalues, method = "BH")

#Finding genes differentially expressed under FDR level 0.05
sum(AdjustedPvalues<0.05)

#DIFFERENTIAL ANALYSIS USING SIGNIFICANCE ANALYSIS OF MICROARRAYS (SAM)
biocLite("impute")
install.packages("samr")

library(impute)
library(samr)

#Preparing data in SAM format
y <- rep(1, ncol(newGeneExpr))
y[C2] = 2
data2 <- list(x=newGeneExpr, y=y, geneid=rownames(newGeneExpr), logged2 = TRUE)
samr.obj <- samr(data2, resp.type = "Two class unpaired", nperms=100)

#Making SAM Plot
delta = 0.4
pdf(file = "WhiteMatterSAMPlot.pdf")
samr.plot(samr.obj, delta)
dev.off()

#Getting P values from SAM
samPValues <- samr.pvalues.from.perms(samr.obj$tt, samr.obj$ttstar)

#USING LIMMA
biocLite("limma")
library(limma)

#Preparing Design Matrix
sampleType <- c(rep("White Matter Control", 6), rep("White Matter HIV", 6))
DM <-model.matrix(~0+factor(sampleType))
colnames(DM) <- c("WhiteMatterControl", "WhiteMatterHIV")

#Fitting the Model
fit <- lmFit(newGeneExpr, DM)
contrast.matrix <- makeContrasts(WhiteMatterControl - WhiteMatterHIV, levels = DM)
fit2 <- contrasts.fit(fit, contrast.matrix)
fit2 <- eBayes(fit2)

#Finding top ten significant genes
Ltop10 <- topTable(fit2, adjust = "BH", number = 10)
limmaAll <- topTable(fit2, adjust = "BH", number = nrow(newGeneExpr)) #All DE results
limmaAll2 <- setNames(cbind(rownames(limmaAll), limmaAll, row.names = NULL), c("ID", "logFC", "AveExpr", "t", "P.Value", "adj.P.Val", "B"))
save.image("project.Rdata")

#Gathering gene symbols and descriptions from hgu133a library
biocLite("Biobase")
biocLite("hgu133a.db")

library("hgu133a.db")
affy.symbol <- unlist(as.list(hgu133aSYMBOL))
affy.name <- unlist(as.list(hgu133aGENENAME))
ProbeID <- unlist(limmaAll2["ID"])
anno <- data.frame(PROBE_ID = ProbeID, SYMBOL = affy.symbol[ProbeID], DEFINITION = affy.name[ProbeID], stringsAsFactors = FALSE)
head(anno)
Results <- data.frame(limmaAll2, newGeneExpr, Description = affy.name[ProbeID])
head(Results)

install.packages("xlsx")
library(xlsx)
write.csv(Results, file = "ProjectResults.csv", row.names = TRUE)

#Annotating the analysis
rpts <- data.frame(Symbol = affy.symbol[ProbeID], limmaAll2, Description = affy.name[ProbeID])
AA <- rpts[,c("Symbol", "t")]

#GENE SET ENRICHMENT ANALYSIS (GSEA)
absmax <- function(z){z[which.max(abs(z))]}
AAmax <- aggregate(AA["t"], by = AA["Symbol"], absmax)

install.packages("dplyr")
library(dplyr)

AAmaxFinal <- arrange(AAmax, desc(t))
write.table(AAmaxFinal, file = "GSE35864_limma_Final.rnk", quote = FALSE, row.names = FALSE)

#Volcano Plot
pdf('VolcanoPlot.pdf')
volcanoplot(fit2, xlab = "Log Fold Change", ylab = "Log Odds")
dev.off()
savehistory(file = "ProjectLast.Rhistory")
