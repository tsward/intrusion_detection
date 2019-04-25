


if [[ $# -ne 1 ]]
then
    >&2 echo "Usage: ${0} [test_file]"
    >&2 echo "    [test_file]        test set arff file (must be in arff_files directory)"
    exit 1
fi



if ! mvn compile; then
    echo "maven compile failed."
    exit 1
fi


if ! mvn exec:java -Dexec.mainClass=com.scoresman.App -Dexec.args="classifyTestFile $1"; then
    echo "App.java run time failure."
    exit 1
fi
