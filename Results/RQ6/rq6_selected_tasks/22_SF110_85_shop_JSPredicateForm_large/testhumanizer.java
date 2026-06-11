@Test(timeout = 4000)
    public void testInvalidJSPredicateFormInit() throws Throwable {
        // Given: A StreamTokenizer with invalid input
        StringReader stringReader = new StringReader("9(^cAoM)");
        StreamTokenizer streamTokenizer = new StreamTokenizer(stringReader);
        JSTerm jSTerm = new JSTerm(streamTokenizer);

        // When: Initializing JSPredicateForm
        // Then: Expect an Error due to invalid syntax
        try {
            jSTerm.JSPredicateFormInit(streamTokenizer);
            fail("Expecting exception: Error");
        } catch (Error e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testStandardizerPredicateForm() throws Throwable {
        // Given: A JSTerm with specific input
        StringReader stringReader = new StringReader("9(^cA)");
        StreamTokenizer streamTokenizer = new StreamTokenizer(stringReader);
        JSTerm jSTerm = new JSTerm(streamTokenizer);
        jSTerm.add((Object) jSTerm);

        // When: Standardizing the predicate form
        JSPredicateForm jSPredicateForm = jSTerm.standarizerPredicateForm();

        // Then: Verify the standardized form
        assertEquals("Standardized form should match expected output", "[9.0, [9.0]]", jSPredicateForm.toString());
    }

    @Test(timeout = 4000)
    public void testCloneAndEquals() throws Throwable {
        // Given: A JSTerm with specific input
        StringReader stringReader = new StringReader("not");
        StreamTokenizer streamTokenizer = new StreamTokenizer(stringReader);
        JSTerm jSTerm = new JSTerm(streamTokenizer);
        jSTerm.add((Object) jSTerm);

        // When: Cloning and checking equality
        JSPredicateForm jSPredicateForm = jSTerm.clonePF();
        jSTerm.makeFunction();
        boolean isEqual = jSTerm.equals(jSPredicateForm);

        // Then: Verify the clone and equality
        assertEquals("Cloned form should have size 2", 2, jSPredicateForm.size());
        assertFalse("Cloned form should not be equal to original", isEqual);
    }

    @Test(timeout = 4000)
    public void testEqualsSameObject() throws Throwable {
        // Given: A JSPredicateForm with specific input
        JSPredicateForm jSPredicateForm = new JSPredicateForm("(mKs=v8 H_)Z");

        // When: Checking equality with itself
        boolean isEqual = jSPredicateForm.equals(jSPredicateForm);

        // Then: Verify equality
        assertTrue("Predicate form should be equal to itself", isEqual);
    }

    @Test(timeout = 4000)
    public void testEqualsDifferentObject() throws Throwable {
        // Given: A JSPredicateForm and a JSTerm
        JSPredicateForm jSPredicateForm = new JSPredicateForm("(mKs=v8 H_)Z");
        JSTerm jSTerm = new JSTerm();

        // When: Checking equality with a different object
        boolean isEqual = jSPredicateForm.equals((JSPredicateForm) jSTerm);

        // Then: Verify inequality
        assertFalse("Predicate form should not be equal to a different object", isEqual);
    }

    @Test(timeout = 4000)
    public void testEqualsNull() throws Throwable {
        // Given: A JSTerm
        JSTerm jSTerm = new JSTerm();

        // When: Checking equality with null
        boolean isEqual = jSTerm.equals((JSPredicateForm) null);

        // Then: Verify inequality
        assertFalse("Predicate form should not be equal to null", isEqual);
    }

    @Test(timeout = 4000)
    public void testMatchesWithSubstitutionFail() throws Throwable {
        // Given: A JSTerm and a JSSubstitution
        StringReader stringReader = new StringReader("not");
        StreamTokenizer streamTokenizer = new StreamTokenizer(stringReader);
        JSSubstitution jSSubstitution = new JSSubstitution();
        JSTerm jSTerm = new JSTerm(streamTokenizer);
        jSTerm.add((Object) jSTerm);
        JSPredicateForm jSPredicateForm = jSTerm.clonePF();
        jSTerm.makeFunction();

        // When: Matching with substitution
        JSSubstitution resultSubstitution = jSTerm.matches(jSPredicateForm, jSSubstitution);

        // Then: Verify the substitution fails
        assertEquals("Cloned form should match expected output", "[%%, [%%]]", jSPredicateForm.toString());
        assertTrue("Substitution should fail", resultSubstitution.fail());
    }

    @Test(timeout = 4000)
    public void testMatchesWithSubstitutionSuccess() throws Throwable {
        // Given: A JSTerm and a JSSubstitution
        StringReader stringReader = new StringReader("not");
        StreamTokenizer streamTokenizer = new StreamTokenizer(stringReader);
        JSSubstitution jSSubstitution = new JSSubstitution();
        JSTerm jSTerm = new JSTerm(streamTokenizer);
        jSTerm.add((Object) jSTerm);
        JSPredicateForm jSPredicateForm = jSTerm.clonePF();

        // When: Matching with substitution
        JSSubstitution resultSubstitution = jSTerm.matches(jSPredicateForm, jSSubstitution);

        // Then: Verify the substitution does not fail
        assertEquals("Cloned form should match expected output", "[%%, [%%]]", jSPredicateForm.toString());
        assertFalse("Substitution should not fail", resultSubstitution.fail());
    }

    @Test(timeout = 4000)
    public void testMatchesDifferentTerms() throws Throwable {
        // Given: Two JSTerms with different inputs
        StringReader stringReader = new StringReader("Q\nS N@G");
        StreamTokenizer streamTokenizer = new StreamTokenizer(stringReader);
        JSSubstitution jSSubstitution = new JSSubstitution();
        JSTerm jSTerm0 = new JSTerm(streamTokenizer);
        JSTerm jSTerm1 = new JSTerm(streamTokenizer);

        // When: Matching different terms
        JSSubstitution resultSubstitution = jSTerm0.matches((JSPredicateForm) jSTerm1, jSSubstitution);

        // Then: Verify the substitution fails
        assertTrue("Substitution should fail for different terms", resultSubstitution.fail());
    }

    @Test(timeout = 4000)
    public void testMatchesEmptyPredicateForm() throws Throwable {
        // Given: A JSTerm and an empty JSPredicateForm
        StringReader stringReader = new StringReader("Z");
        StreamTokenizer streamTokenizer = new StreamTokenizer(stringReader);
        JSTerm jSTerm = new JSTerm(streamTokenizer);
        JSSubstitution jSSubstitution = new JSSubstitution();
        JSPredicateForm jSPredicateForm = new JSPredicateForm();

        // When: Matching with an empty predicate form
        JSSubstitution resultSubstitution = jSTerm.matches(jSPredicateForm, jSSubstitution);

        // Then: Verify the substitution fails
        assertTrue("Substitution should fail for empty predicate form", resultSubstitution.fail());
    }

    @Test(timeout = 4000)
    public void testApplySubstitutionPF() throws Throwable {
        // Given: A JSPredicateForm with specific input
        JSPredicateForm jSPredicateForm = new JSPredicateForm("(mKs=v8o H_:)Z");

        // When: Applying a null substitution
        JSPredicateForm resultPredicateForm = jSPredicateForm.applySubstitutionPF((JSSubstitution) null);

        // Then: Verify the result is a new object and matches expected output
        assertNotSame("Result should be a new object", resultPredicateForm, jSPredicateForm);
        assertEquals("Result should match expected output", "[mKs=v8o, [H:]]", resultPredicateForm.toString());
    }

    @Test(timeout = 4000)
    public void testToStrEmpty() throws Throwable {
        // Given: An empty JSPredicateForm
        JSPredicateForm jSPredicateForm = new JSPredicateForm();

        // When: Converting to string
        StringBuffer stringBuffer = jSPredicateForm.toStr();

        // Then: Verify the string is empty
        assertEquals("String representation should be empty", 0, stringBuffer.length());
    }

    @Test(timeout = 4000)
    public void testToStrNonEmpty() throws Throwable {
        // Given: A JSPredicateForm with specific input
        JSPredicateForm jSPredicateForm = new JSPredicateForm("(mKJs=v8o H)Z");

        // When: Converting to string
        StringBuffer stringBuffer = jSPredicateForm.toStr();

        // Then: Verify the string length matches expected
        assertEquals("String representation length should match expected", 12, stringBuffer.length());
    }

    @Test(timeout = 4000)
    public void testPrintEmpty() throws Throwable {
        // Given: An empty JSPredicateForm
        JSPredicateForm jSPredicateForm = new JSPredicateForm();

        // When: Printing the predicate form
        jSPredicateForm.print();

        // Then: Verify the predicate form is empty
        assertTrue("Predicate form should be empty", jSPredicateForm.isEmpty());
    }

    @Test(timeout = 4000)
    public void testPrintNonEmpty() throws Throwable {
        // Given: A JSPredicateForm with specific input
        JSPredicateForm jSPredicateForm = new JSPredicateForm("(mKs=v8o H_:)Z");

        // When: Printing the predicate form
        jSPredicateForm.print();

        // Then: Verify the predicate form is not empty
        assertFalse("Predicate form should not be empty", jSPredicateForm.isEmpty());
    }

    @Test(timeout = 4000)
    public void testInvalidJSPredicateFormConstruction() throws Throwable {
        // Given: Invalid input for JSPredicateForm
        // When: Constructing JSPredicateForm
        // Then: Expect an Error due to invalid syntax
        try {
            new JSPredicateForm("(mKVZs=vF UDZ");
            fail("Expecting exception: Error");
        } catch (Error e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testMatchesWithSelf() throws Throwable {
        // Given: A JSPredicateForm with specific input
        JSPredicateForm jSPredicateForm = new JSPredicateForm("(mKs=v8o H)Z");
        JSSubstitution jSSubstitution = new JSSubstitution();

        // When: Matching with itself
        JSSubstitution resultSubstitution = jSPredicateForm.matches(jSPredicateForm, jSSubstitution);

        // Then: Verify the substitution does not fail
        assertFalse("Substitution should not fail when matching with itself", resultSubstitution.fail());
    }

    @Test(timeout = 4000)
    public void testInvalidJSPredicateFormConstruction2() throws Throwable {
        // Given: Invalid input for JSPredicateForm
        // When: Constructing JSPredicateForm
        // Then: Expect an Error due to invalid syntax
        try {
            new JSPredicateForm("(mKs=v8 ");
            fail("Expecting exception: Error");
        } catch (Error e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testInvalidJSPredicateFormConstruction3() throws Throwable {
        // Given: Invalid input for JSPredicateForm
        // When: Constructing JSPredicateForm
        // Then: Expect an Error due to invalid syntax
        try {
            new JSPredicateForm("(mKs=v8UDZ");
            fail("Expecting exception: Error");
        } catch (Error e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testInvalidJSPredicateFormConstruction4() throws Throwable {
        // Given: Invalid input for JSPredicateForm
        // When: Constructing JSPredicateForm
        // Then: Expect an Error due to invalid syntax
        try {
            new JSPredicateForm("(!mKs=8qHEZ");
            fail("Expecting exception: Error");
        } catch (Error e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testInvalidJSPredicateFormConstruction5() throws Throwable {
        // Given: Invalid input for JSPredicateForm
        // When: Constructing JSPredicateForm
        // Then: Expect an Error due to invalid syntax
        try {
            new JSPredicateForm("(!4mk:s#@-[e;z");
            fail("Expecting exception: Error");
        } catch (Error e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testInvalidStreamTokenizerConstruction() throws Throwable {
        // Given: Invalid input for StreamTokenizer
        StringReader stringReader = new StringReader("91(c)");
        StreamTokenizer streamTokenizer = new StreamTokenizer(stringReader);
        stringReader.read();

        // When: Constructing JSPredicateForm with invalid tokenizer
        // Then: Expect an Error due to invalid syntax
        try {
            new JSPredicateForm(streamTokenizer);
            fail("Expecting exception: Error");
        } catch (Error e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testInvalidJSPredicateFormConstruction6() throws Throwable {
        // Given: Invalid input for JSPredicateForm
        // When: Constructing JSPredicateForm
        // Then: Expect an Error due to invalid syntax
        try {
            new JSPredicateForm("(");
            fail("Expecting exception: Error");
        } catch (Error e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testInvalidJSPredicateFormConstruction7() throws Throwable {
        // Given: Invalid input for JSPredicateForm
        // When: Constructing JSPredicateForm
        // Then: Expect an Error due to invalid syntax
        try {
            new JSPredicateForm("call");
            fail("Expecting exception: Error");
        } catch (Error e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testNullStreamTokenizerConstruction() throws Throwable {
        // Given: Null StreamTokenizer
        // When: Constructing JSPredicateForm
        // Then: Expect an Error due to null tokenizer
        try {
            new JSPredicateForm((StreamTokenizer) null);
            fail("Expecting exception: Error");
        } catch (Error e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testEqualsWithDifferentObject() throws Throwable {
        // Given: A JSPredicateForm and a JSTerm with different inputs
        JSPredicateForm jSPredicateForm = new JSPredicateForm("(mKs~8=H_)kZ");
        JSTerm jSTerm = new JSTerm();
        jSTerm.add((Object) "(mKs~8=H_)kZ");

        // When: Checking equality with a different object
        boolean isEqual = jSPredicateForm.equals((JSPredicateForm) jSTerm);

        // Then: Verify inequality
        assertFalse("Predicate form should not be equal to a different object", isEqual);
    }

    @Test(timeout = 4000)
    public void testNullStringConstruction() throws Throwable {
        // Given: Null input for JSPredicateForm
        // When: Constructing JSPredicateForm
        JSPredicateForm jSPredicateForm = new JSPredicateForm((String) null);

        // Then: Verify the predicate form is empty
        assertEquals("Predicate form should be empty", 0, jSPredicateForm.size());
    }

    @Test(timeout = 4000)
    public void testValidStreamTokenizerConstruction() throws Throwable {
        // Given: Valid input for StreamTokenizer
        StringReader stringReader = new StringReader("(!m4t:4&$OV;-);&");
        StreamTokenizer streamTokenizer = new StreamTokenizer(stringReader);

        // When: Constructing JSPredicateForm
        JSPredicateForm jSPredicateForm = new JSPredicateForm(streamTokenizer);

        // Then: Verify the predicate form matches expected output
        assertEquals("Predicate form should match expected output", "[!m4t:4OV;-]", jSPredicateForm.toString());
    }

    @Test(timeout = 4000)
    public void testMatchesWithNull() throws Throwable {
        // Given: An empty JSPredicateForm
        JSPredicateForm jSPredicateForm = new JSPredicateForm();

        // When: Matching with null
        // Then: Expect a NullPointerException
        try {
            jSPredicateForm.matches((JSPredicateForm) null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }