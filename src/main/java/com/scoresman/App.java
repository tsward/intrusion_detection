package com.scoresman;



/**
 * App
 *
 */
 
import java.util.Random;
import weka.classifiers.Classifier;
import weka.classifiers.Evaluation;
import weka.classifiers.bayes.NaiveBayes;
import weka.core.Instances;
import weka.core.Utils;
import weka.core.converters.ConverterUtils.DataSource;
import java.io.File;
import java.io.*;


 
public class App 
{
    
    private final static String trainFile = "train.arff";
    
    private static void classifyTestFile(String testFile, int folds, int runs) {
        
        IDSClassifier nbIDS = new IDSClassifier(IDSClassifier.TYPES.NAIVE_BAYES);
        nbIDS.buildClassifier("arff_files/" + trainFile);
        //System.out.println("nbIDS: " + nbIDS);
        //nbIDS.evaluateTrainingSet(folds, runs);
        nbIDS.setTestSet(testFile);
        //nbIDS.evaluateModel(true);
        nbIDS.evaluateModel(true);
        //nbIDS.evaluateTestResults(true);
        
        System.out.println("\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n");
        
        IDSClassifier tree = new IDSClassifier(IDSClassifier.TYPES.J48_TREE);
        tree.buildClassifier("arff_files/" + trainFile);
        //System.out.println("tree: " + tree);
        //tree.evaluateTrainingSet(folds, runs);
        tree.setTestSet(testFile);
        tree.evaluateModel(true);
        //tree.evaluateTestResults(true);
        
    }
    
    private static void classifyRunTimeInstance(String nLogins, String containsSemi, String ssnLen, String groundTruth, int folds, int runs) {
        
        IDSClassifier nbIDS = new IDSClassifier(IDSClassifier.TYPES.NAIVE_BAYES);
        nbIDS.buildClassifier("arff_files/" + trainFile);
        //System.out.println("nbIDS: " + nbIDS);
        //nbIDS.evaluateTrainingSet(folds, runs);
        //nbIDS.setTestSet(testFile);
        //nbIDS.evaluateModel(true);
        //nbIDS.evaluateModel(true);
        //nbIDS.evaluateTestResults(true);
        String result = nbIDS.classifyRunTimeInstance(nLogins, containsSemi, ssnLen, groundTruth);
        try {
            FileWriter fw = new FileWriter("cur_runtime_classification.txt");
            BufferedWriter bw = new BufferedWriter(fw);
            bw.write(result);
            bw.close();
        } catch(IOException ioe) {}
        
        System.out.println("\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n");
        
        
        IDSClassifier tree = new IDSClassifier(IDSClassifier.TYPES.J48_TREE);
        tree.buildClassifier("arff_files/" + trainFile);
        //System.out.println("tree: " + tree);
        //tree.evaluateTrainingSet(folds, runs);
        //tree.setTestSet(testFile);
        //tree.evaluateModel(true);
        //tree.evaluateTestResults(true);
        
        
    }
    
    /*
    private static boolean invalidArgs(String[] args) {
        
        // NOTE: already tested in bash script
        if(args.length != 2) {
            return true;
        }
        
        String trainFile = args[0];
        String testFile = args[1];
        File f = new File("arff_files/" + trainFile);
        if(!f.exists()) { 
            System.out.println("Train file: " + trainFile + " not found in arff_files directory.");
            return true;
        }
        f = new File("arff_files/" + testFile);
        if(!f.exists()) { 
            System.out.println("Test file: " + testFile + " not found in arff_files directory.");
            return true;
        }
        
        return false;
    }
    */
    
    public static void main(String[] args) {
        
        System.out.println("======Intrusion Detection Main App=======");
        /* TODO
        if(invalidArgs(args)) {
            System.err.println("Invalid Args.");
            return;
        } 
        */
        
        
        if(! new File("./arff_files/train.arff").exists()) {
            System.out.println("ERROR: training set arff file \"train.arff\" not found in arff_files directory.");
            return;
        }
        
        String action = args[0];
        if(action.equals("classifyTestFile")) {
            
            if(args.length < 2) {
                System.out.println("Invalid weka test file entry");
                return;
            }
            
            String testFile = "arff_files/" + args[1];
            
            if(! new File(testFile).exists()) {
                System.out.println("ERROR: test set arff file \"" + testFile + " not found in arff_files directory.");
                return;
            }
            
            int folds = 10;
            int runs = 30;
            classifyTestFile(testFile, folds, runs);
        }
        else if(action.equals("runtimeClassification")) {
            String nLogins = args[1];
            String containsSemi = args[2];
            String ssnLen = args[3];
            String groundTruth = args[4];
            int folds = 10;
            int runs = 30;
            classifyRunTimeInstance(nLogins, containsSemi, ssnLen, groundTruth, folds, runs);
        }
        else { 
            System.out.println("UNKNOWN ACTION: " + action);
            return;
        }
        
        System.out.println("=========================================");
    }
    
}
