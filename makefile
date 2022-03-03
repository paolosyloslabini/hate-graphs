CXX       =g++
CXXFLAGS  =  -fpermissive -Wl,--no-as-needed -m64 -std=c++11 -fopenmp
INCLUDE = -I include

TARGET=main

all: $(TARGET)

$(TARGET): $(TARGET).c
	$(CXX) $(CXXFLAGS) $(INCLUDE) -o $(TARGET) $(TARGET).cpp
 
clean:
	$(RM) $(TARGET)