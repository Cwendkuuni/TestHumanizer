package org.scribe.model;

import org.scribe.utils.*;

public class Verifier
{
    private final String value;
    
    public Verifier(final String value) {
        Preconditions.checkNotNull(value, "Must provide a valid string as verifier");
        this.value = value;
    }
    
    public String getValue() {
        return this.value;
    }
}
