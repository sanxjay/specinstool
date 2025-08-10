#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "instruction.h"

#define INSTRUCTION_STRUCT instruction_data

void print_usage() {
    printf("Usage: ./headertoyaml <output_yaml_file>\n");
}


void print_yaml_multiline(FILE *f, const char *indent, const char *text) {
    if (!text || !*text) return;
    const char *line_start = text;
    const char *newline_pos;
    while ((newline_pos = strchr(line_start, '\n')) != NULL) {
        // Only print the line if it's not empty
        if (newline_pos > line_start) {
            fprintf(f, "%s%.*s\n", indent, (int)(newline_pos - line_start), line_start);
        } else {
            // Print empty line without extra indentation
            fprintf(f, "\n");
        }
        line_start = newline_pos + 1;
    }
    // Print the last line if it's not empty
    if (*line_start != '\0') {
        fprintf(f, "%s%s\n", indent, line_start);
    }
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        print_usage();
        return 1;
    }

    char *output_filename = argv[1];
    FILE *yaml_file = fopen(output_filename, "w");
    if (yaml_file == NULL) {
        perror("Error opening output file");
        return 1;
    }

    // Write YAML comments from the struct
    for (int i = 0; i < INSTRUCTION_STRUCT.num_comments; i++) {
        fprintf(yaml_file, "%s\n", INSTRUCTION_STRUCT.comments[i]);
    }
    if (INSTRUCTION_STRUCT.num_comments > 0) {
        fprintf(yaml_file, "\n");
    }

    // Output YAML fields in the correct order
    fprintf(yaml_file, "$schema: \"%s\"\n", INSTRUCTION_STRUCT.schema);
    fprintf(yaml_file, "kind: %s\n", INSTRUCTION_STRUCT.kind);
    fprintf(yaml_file, "name: %s\n", INSTRUCTION_STRUCT.name);
    fprintf(yaml_file, "long_name: %s\n", INSTRUCTION_STRUCT.long_name);
    fprintf(yaml_file, "description: |\n");
    print_yaml_multiline(yaml_file, "  ", INSTRUCTION_STRUCT.description);
    fprintf(yaml_file, "definedBy: %s\n", INSTRUCTION_STRUCT.definedBy);
    fprintf(yaml_file, "assembly: %s\n", INSTRUCTION_STRUCT.assembly);
    // encoding
    fprintf(yaml_file, "encoding:\n");
    fprintf(yaml_file, "  match: %s\n", INSTRUCTION_STRUCT.encoding.match);
    fprintf(yaml_file, "  variables:\n");
    for (int i = 0; i < INSTRUCTION_STRUCT.encoding.num_variables; i++) {
        fprintf(yaml_file, "    - name: %s\n", INSTRUCTION_STRUCT.encoding.variables[i].name);
        fprintf(yaml_file, "      location: %s\n", INSTRUCTION_STRUCT.encoding.variables[i].location);
    }
    // access
    fprintf(yaml_file, "access:\n");
    fprintf(yaml_file, "  s: %s\n", INSTRUCTION_STRUCT.access.s);
    fprintf(yaml_file, "  u: %s\n", INSTRUCTION_STRUCT.access.u);
    fprintf(yaml_file, "  vs: %s\n", INSTRUCTION_STRUCT.access.vs);
    fprintf(yaml_file, "  vu: %s\n", INSTRUCTION_STRUCT.access.vu);
    // data_independent_timing
    fprintf(yaml_file, "data_independent_timing: %s\n", INSTRUCTION_STRUCT.data_independent_timing ? "true" : "false");
    // hints
    if (INSTRUCTION_STRUCT.num_hints > 0) {
        fprintf(yaml_file, "hints:\n");
        for (int i = 0; i < INSTRUCTION_STRUCT.num_hints; i++) {
            fprintf(yaml_file, "  - { $ref: %s }\n", INSTRUCTION_STRUCT.hints[i].ref);
        }
    }
    // pseudoinstructions
    if (INSTRUCTION_STRUCT.num_pseudoinstructions > 0) {
        fprintf(yaml_file, "pseudoinstructions:\n");
        for (int i = 0; i < INSTRUCTION_STRUCT.num_pseudoinstructions; i++) {
            fprintf(yaml_file, "  - when: %s\n", INSTRUCTION_STRUCT.pseudoinstructions[i].when);
            fprintf(yaml_file, "    to: %s\n", INSTRUCTION_STRUCT.pseudoinstructions[i].to);
        }
    }
    // operation()
    if (INSTRUCTION_STRUCT.operation[0]) {
        fprintf(yaml_file, "operation(): |\n");
        print_yaml_multiline(yaml_file, "  ", INSTRUCTION_STRUCT.operation);
    }
    // sail()
    if (INSTRUCTION_STRUCT.sail[0]) {
        fprintf(yaml_file, "sail(): |\n");
        print_yaml_multiline(yaml_file, "  ", INSTRUCTION_STRUCT.sail);
    }

    fclose(yaml_file);
    // printf("YAML file '%s' created successfully.\n", output_filename);
    return 0;
}