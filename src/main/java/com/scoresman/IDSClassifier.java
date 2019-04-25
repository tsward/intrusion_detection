
package com.scoresman;



/**
 * IDS classifier
 *
 */

 
import weka.classifiers.Classifier;
import weka.classifiers.bayes.NaiveBayes; 
import weka.classifiers.Evaluation; 
import weka.classifiers.trees.J48;
import weka.core.Instances;
import weka.core.Instance;
import java.io.FileReader;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.*;
import java.util.Random;
import weka.core.Utils;

 
public class IDSClassifier {  
    
    
    private Instances trainingSet;
    private Instances testSet;
    
    private Classifier classifier;
    private TYPES type;
    
    
    public enum TYPES {
        NAIVE_BAYES, J48_TREE // , MORE???
    }
    
    public IDSClassifier(TYPES type) {
        super();
        this.type = type;
        if(type == TYPES.NAIVE_BAYES)
            this.classifier = new NaiveBayes();
        else if(type == TYPES.J48_TREE) 
            this.classifier = new J48();
    }
    

    public void buildClassifier(String trainingFileDir) {
        try {
            FileReader reader = new FileReader(trainingFileDir);
            this.trainingSet = new Instances(new java.io.BufferedReader(reader));
            this.trainingSet.setClassIndex(this.trainingSet.numAttributes() - 1); 
            classifier.buildClassifier(this.trainingSet);
            this.testSet = null;
        } catch(java.io.IOException ioe) {
            System.err.println("IOException: " + ioe);
            System.exit(9);
        }  catch(Exception e) {
            System.err.println("Exception" + e);
            System.exit(9);
        }  
    }


    public void evaluateTrainingSet(int folds, int runs) {
        System.out.println("#seed \t correctly instances \t percentage of corrects\n");
        for (int i = 1; i <= runs; i++) {
            try {
                Evaluation eval = new Evaluation(trainingSet);
                eval.crossValidateModel(this.classifier, this.trainingSet, folds, new Random(i));

                System.out.println("#" + i + "\t" + summary(eval));
            }
            catch(Exception e) {
                System.out.println("Exception: " + e);
                System.exit(9);
            }
        }
    }
    
    public void setTestSet(String testFileDir) {
        try {
            FileReader reader = new FileReader(testFileDir);
            this.testSet = new Instances(new java.io.BufferedReader(reader));
            this.testSet.setClassIndex(this.testSet.numAttributes() - 1);
        } catch(Exception e) {
            System.out.println("setTestSet Exception: " + testFileDir + ", " + e);
        }
        
    }
    
    public void evaluateTestResults(boolean full) {
        try {
            // TODO: figure out how to get useful graphs out of this data!
            BufferedWriter out = new BufferedWriter(new FileWriter("evaluate_test_results.txt"));
            if(full) {
                for(int i = 0; i < this.testSet.numInstances(); i++) {
                    Instance instance = this.testSet.instance(i);
                    //System.out.println(instance);
                    double index = classifier.classifyInstance(instance);
                    String className = this.trainingSet.attribute(this.testSet.numAttributes() - 1).value((int) index);
                    //System.out.println(className);
                    out.write(instance.toString());
                    out.newLine();
                }
                out.close();
            }
        } catch(Exception e) {
            System.out.println("evaluateModel Exception: " + e);
        }
        
    }
    
    public void evaluateModel(boolean full) {
        try {
            Evaluation eval = new Evaluation(this.trainingSet);
            eval.evaluateModel(this.classifier, this.testSet);
            /** Print the algorithm summary */
            System.out.println(eval.toSummaryString());
            System.out.print(" the expression for the input data as per alogorithm is ");
            System.out.println(this);
            // TODO: output to a file for testing (could just get it from arff file...)
            //BufferedWriter out = new BufferedWriter(new FileWriter("weka_output.txt"));
            if(full) {
                for(int i = 0; i < this.trainingSet.numInstances(); i++) {
                    Instance instance = this.trainingSet.instance(i);
                    //System.out.println(instance);
                    double index = classifier.classifyInstance(instance);
                    String className = this.trainingSet.attribute(this.testSet.numAttributes() - 1).value((int) index);
                    System.out.println(className);
                    //out.write(instance.toString());
                    //out.newLine();
                }
                //out.close();
            }
        } catch(Exception e) {
            System.out.println("evaluateModel Exception: " + e);
        }
        
    }
    
    public String classifyRunTimeInstance(String nLogins, String containsSemi, String ssnLen, String groundTruth) {
        
        String header = "%\n" + 
                "@relation \'safe_or_malicious\'\n" + 
                "@attribute \'n_logins\' numeric\n" +
                "@attribute \'pswd_contains_semi\' {\'yes\',\'no\'}\n" + 
                "@attribute \'ssn_len\' numeric\n" +
                "@attribute \'is_malicious\' {\'MALICIOUS\',\'SAFE\'}\n" +
                "@data\n%\n";
        String tmpArffFile = "arff_files/rtc_arff.txt";
        try {
            FileWriter fw = new FileWriter(tmpArffFile);
            BufferedWriter bw = new BufferedWriter(fw);
            bw.write(header);
            String line = nLogins + " " + containsSemi + " " + ssnLen + " " + groundTruth + "\n";
            bw.write(line);
            bw.close();
        } catch(IOException ioe) {}
        
        String ret = "";
        try {
            FileReader reader = new FileReader(tmpArffFile);
            Instances instances = new Instances(new java.io.BufferedReader(reader));
            instances.setClassIndex(instances.numAttributes() - 1);
            Instance instance = instances.instance(0);
            double index = classifier.classifyInstance(instance);
            ret = this.trainingSet.attribute(instances.numAttributes() - 1).value((int) index);
            System.out.println(ret);
        } catch(Exception e) { 
            System.err.println("Error reading temp file for run time classification. " + e);
            ret = "run time classification error";
        }
        // delete the temp file
        new File(tmpArffFile).delete();
        return ret;
    }
    
    private static String summary(Evaluation eval){
        return Utils.doubleToString(eval.correct(), 12, 4) + "\t " +
                Utils.doubleToString(eval.pctCorrect(), 12, 4) + "%";
    }
    
    public String toString() {
        String ret = "";
        ret += this.classifier.toString();
        return ret;
    }
    
    public static void main( String[] args )
    {

        //new NBayes("/home/scores-man/Desktop/labor.arff");
        
    }
}




//loader.setQuery("select * from data_training");
//Instances data = loader.getDataSet();
//Add the following
//data.setClassIndex(data.numAttributes() - 1);
        
        
        
        
