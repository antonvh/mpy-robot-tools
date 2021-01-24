# Micropython robot tools #

This is a collection of classes and methods that help you to animate robots. They are specifically aimed at LEGO MINDSTORMS and SPIKE Prime robots, although the classes are abstract enough to be useful elsewhere. The functionality is documented inside the code. Here are just the main usages. For in-depth articles see my blog on [antonsmindstorms.com](https://antonsmindstorms.com). 

## Installation ##

Sadly the official LEGO apps do not allow multi-file projects. The only way to use these classes is to copy them and past them in your script.


## Overview of the tools ##

### Mechanism ###
- AMHTimer() - This is a timer class that returns milliseconds by default. 
- Mechanism(motors, time_functions) - Calculates pwms based on motor functions.

### Display tools ###
- image_99(int) - Returns a 5x5 matrix display string to show numbers up to 99 in one screen.