package com.testhumanizer.examples;

public class Calculator {

    private int memory = 0;

    public int add(int a, int b) {
        return a + b;
    }

    public int subtract(int a, int b) {
        return a - b;
    }

    public int divide(int numerator, int denominator) {
        if (denominator == 0) {
            throw new IllegalArgumentException("Denominator cannot be zero");
        }
        return numerator / denominator;
    }

    public boolean isEven(int value) {
        return value % 2 == 0;
    }

    public void store(int value) {
        this.memory = value;
    }

    public int recall() {
        return this.memory;
    }

    public void clear() {
        this.memory = 0;
    }
}
