# lstm-dsynt

#### Required software

 * A C++ compiler supporting the [C++11 language standard](https://en.wikipedia.org/wiki/C%2B%2B11)
 * [Boost](http://www.boost.org/) libraries
 * [Eigen](http://eigen.tuxfamily.org) (newer versions strongly recommended)
 * [CMake](http://www.cmake.org/)
 * [gcc](https://gcc.gnu.org/gcc-5/) (only tested with gcc version 5.3.0, may be incompatible with earlier versions)

#### Build instructions

    mkdir build
    cd build
    cmake .. -DEIGEN3_INCLUDE_DIR=/path/to/eigen
    make -j2

#### Train a parsing model


First, run goldParser.py to produce the oracle file. Second run the parser with the following command:

  *parser/lstm-parse -T SpanishTreebank/train-oracle.txt -D SpanishTreebank/development-oracle.txt --hidden_dim 100 --lstm_input_dim 100 --pretrained_dim 64 -w SpanishTreebank/vec.txt --rel_dim 20 --action_dim 20 -M -P -t


#### Parsing

  *parser/lstm-parse -T SpanishTreebank/train-oracle.txt -D SpanishTreebank/development-oracle.txt --hidden_dim 100 --lstm_input_dim 100 --pretrained_dim 64 -w SpanishTreebank/vec.txt --rel_dim 20 --action_dim 20 -M -P -m <parameters-file>


#### License

This software is released under the terms of the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).
