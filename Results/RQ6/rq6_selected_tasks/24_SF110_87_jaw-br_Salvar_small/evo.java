@Test(timeout = 4000)
  public void test0()  throws Throwable  {
      ProcessarEntidadesTabela processarEntidadesTabela0 = new ProcessarEntidadesTabela();
      Salvar salvar0 = null;
      try {
        salvar0 = new Salvar(processarEntidadesTabela0, 0);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("jaw.entrada.Salvar", e);
      }
  }

  @Test(timeout = 4000)
  public void test1()  throws Throwable  {
      Salvar salvar0 = null;
      try {
        salvar0 = new Salvar((ProcessarEntidades) null, 1);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("jaw.entrada.Salvar", e);
      }
  }