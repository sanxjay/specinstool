#!/bin/bash

SRC="$(dirname "$0")/../src"
TEST="$(dirname "$0")"
OUT="$(dirname "$0")/../output"


#Base URL for the YAML files
BASE_URL="https://raw.githubusercontent.com/riscv-software-src/riscv-unified-db/main/spec/std/isa/inst"

#Get the file path from the first command-line argument
if [ -z "$1" ]; then
    echo "Usage: $0 <path_to_yaml_file>"
    echo "Example: $0 /C/c.add.yaml"
    exit 1
fi

user_path="/$1"

#Construct the full URL
full_url="$BASE_URL$user_path"

#Extract the filename from the path
filename=$(basename "$user_path")

#Download the file
echo "Downloading $filename..."
curl -s -L "$full_url" -o "$TEST/$filename"

#Check if the download was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to download the YAML file."
    exit 1
fi

#Check if file is valid
if grep -q '404: Not Found' $TEST/$filename; then
    echo "Error: File not found (404)."
    rm $TEST/$filename #removing invalid file (possibly misspelled)
    exit 1
fi

echo "Downloaded $filename successfully."


#Generate the header file
python3 "$SRC/yaml_to_header.py" "$TEST/$filename" $SRC/instruction.h

#Compile the C code
gcc $SRC/headertoyaml.c -o $SRC/headertoyaml

#Run the executable
$SRC/headertoyaml $OUT/output.yaml


#Check if the output file exists
if [ ! -f "$OUT/output.yaml" ]; then
    echo "Failed to create output YAML file."
    exit 1
fi

echo "Output file output.yaml generated."

#Loop

#Convert the generated YAML back to a new header file
echo "Converting output.yaml to instruction.h..."
python3 $SRC/yaml_to_header.py $OUT/output.yaml $SRC/instruction.h

#Compile the C code with the new header
gcc $SRC/headertoyaml.c -o $SRC/headertoyaml

#Run the second executable
$SRC/headertoyaml $OUT/output2.yaml


echo "Output file output2.yaml emitted."

#Removing the C executable
rm $SRC/headertoyaml

#Compare the two YAML files
echo "Comparing output.yaml and output2.yaml..."

#Checking whether created yaml files are same or not.
if diff -q $OUT/output.yaml $OUT/output2.yaml; then
    echo "Success: The generated and emitted YAML files are identical."
else
    echo "Failure: The YAML files are different."
fi