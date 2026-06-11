@Test(timeout = 4000)
    public void testConstructorWithNullProcessarEntidadesTabela() throws Throwable {
        // Given: A ProcessarEntidadesTabela instance
        ProcessarEntidadesTabela processarEntidadesTabela = new ProcessarEntidadesTabela();

        // When: Initializing Salvar with a non-null ProcessarEntidadesTabela and a specific save type
        // Then: Expect a NullPointerException due to uninitialized dependencies
        try {
            Salvar salvar = new Salvar(processarEntidadesTabela, 1844);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Verify that the exception is thrown from the expected class
            verifyException("jaw.entrada.Salvar", e);
        }
    }

    @Test(timeout = 4000)
    public void testConstructorWithNullProcessarEntidades() throws Throwable {
        // Given: A null ProcessarEntidades instance
        ProcessarEntidades processarEntidades = null;

        // When: Initializing Salvar with a null ProcessarEntidades and a specific save type
        // Then: Expect a NullPointerException due to null ProcessarEntidades
        try {
            Salvar salvar = new Salvar(processarEntidades, 38);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Verify that the exception is thrown from the expected class
            verifyException("jaw.entrada.Salvar", e);
        }
    }