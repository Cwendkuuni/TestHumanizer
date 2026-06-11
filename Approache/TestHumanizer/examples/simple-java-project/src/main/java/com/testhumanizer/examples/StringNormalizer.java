package com.testhumanizer.examples;

public class StringNormalizer {

    public String normalize(String input) {
        if (input == null) {
            return "";
        }

        return input.trim().toLowerCase();
    }

    public boolean isBlank(String input) {
        return input == null || input.trim().isEmpty();
    }

    public String repeat(String input, int times) {
        if (input == null) {
            throw new IllegalArgumentException("Input cannot be null");
        }

        if (times < 0) {
            throw new IllegalArgumentException("Times cannot be negative");
        }

        StringBuilder builder = new StringBuilder();
        for (int i = 0; i < times; i++) {
            builder.append(input);
        }

        return builder.toString();
    }

    public String firstWord(String input) {
        if (isBlank(input)) {
            return "";
        }

        String normalized = input.trim();
        int firstSpace = normalized.indexOf(" ");

        if (firstSpace == -1) {
            return normalized;
        }

        return normalized.substring(0, firstSpace);
    }
}
