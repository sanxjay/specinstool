# RISC-V UDB CodeGen Challenge

**Automated toolchain converting RISC-V UDB instruction YAML → C header → YAML, verifying round-trip consistency.**

##  Structure

```
src/      # Source code
  yaml_to_header.py   # YAML → C header
  headertoyaml.c      # C header → YAML
  instruction.h       # Sample header template

test/     # Test runner
  run_test.sh         # Automates conversion & verification

output/   # Generated and sample outputs
```

## Requirements

* Python 3
* GCC
* curl

Install Python dependency (yes only one library) :

```bash
pip install -r requirements.txt
```

## Usage

Clone the project onto your local desktop:

```bash
git clone https://github.com/sanxjay/specinstool
```

From the project root:

```bash
./test/run_test.sh FOLDER/TEST.yaml
```

Replace `FOLDER/TEST.yaml` with the path to a YAML file from the [riscv-unified-db](https://github.com/riscv-software-src/riscv-unified-db/tree/main/spec/std/isa/inst) 

For example - to run this test on `c.add.yaml` file under the folder `C` :-
```
./test/run_test.sh C/c.add.yaml
```

##  Process

1. Download YAML from RISC-V UDB (spec/sta/isa/inst)
2. Convert YAML to C header. (via Python script)
3. Convert the C header back to YAML (via C executable)
4. Steps 2-3 again but this time emitted YAML is taken.
5. Compare results to ensure data consistency

```
[ RISC-V UDB YAML ]
       |
       v
( yaml_to_header.py )
       |
       v
[   C Header File   ]
       |
       v
(  headertoyaml.c   )
       |
       v
[  Generated YAML   ]
       |
       v
( yaml_to_header.py )
       |
       v
[   C Header File   ]
       |
       v
(  headertoyaml.c   )
       |
       v
[  Emitted YAML     ]
       |
       v
(   diff command    )
       |
       v
[   Same or Not     ]
```

##  Developed on
- Python 3.13.5
- GCC 15.1.1