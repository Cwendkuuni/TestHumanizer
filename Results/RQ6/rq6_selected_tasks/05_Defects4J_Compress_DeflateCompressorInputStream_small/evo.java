@Test(timeout = 4000)
  public void test0()  throws Throwable  {
      byte[] byteArray0 = new byte[7];
      ByteArrayInputStream byteArrayInputStream0 = new ByteArrayInputStream(byteArray0, 0, 0);
      DeflateCompressorInputStream deflateCompressorInputStream0 = new DeflateCompressorInputStream(byteArrayInputStream0);
      int int0 = deflateCompressorInputStream0.read(byteArray0, 0, 0);
      assertEquals(0, int0);
  }

  @Test(timeout = 4000)
  public void test1()  throws Throwable  {
      PipedInputStream pipedInputStream0 = new PipedInputStream();
      DeflateParameters deflateParameters0 = new DeflateParameters();
      deflateParameters0.setWithZlibHeader(false);
      DeflateCompressorInputStream deflateCompressorInputStream0 = new DeflateCompressorInputStream(pipedInputStream0, deflateParameters0);
      assertEquals(0, deflateCompressorInputStream0.getCount());
  }

  @Test(timeout = 4000)
  public void test2()  throws Throwable  {
      PipedInputStream pipedInputStream0 = new PipedInputStream();
      DeflateCompressorInputStream deflateCompressorInputStream0 = new DeflateCompressorInputStream(pipedInputStream0);
      int int0 = deflateCompressorInputStream0.available();
      assertEquals(1, int0);
  }

  @Test(timeout = 4000)
  public void test3()  throws Throwable  {
      PipedInputStream pipedInputStream0 = new PipedInputStream();
      DeflateCompressorInputStream deflateCompressorInputStream0 = new DeflateCompressorInputStream(pipedInputStream0);
      DeflateCompressorInputStream deflateCompressorInputStream1 = new DeflateCompressorInputStream(deflateCompressorInputStream0);
      try { 
        deflateCompressorInputStream1.read();
        fail("Expecting exception: IOException");
      
      } catch(IOException e) {
         //
         // Pipe not connected
         //
         verifyException("java.io.PipedInputStream", e);
      }
  }

  @Test(timeout = 4000)
  public void test4()  throws Throwable  {
      PipedInputStream pipedInputStream0 = new PipedInputStream();
      DeflateCompressorInputStream deflateCompressorInputStream0 = new DeflateCompressorInputStream(pipedInputStream0);
      long long0 = deflateCompressorInputStream0.skip(0L);
      assertEquals(0L, long0);
  }

  @Test(timeout = 4000)
  public void test5()  throws Throwable  {
      PipedInputStream pipedInputStream0 = new PipedInputStream();
      DeflateCompressorInputStream deflateCompressorInputStream0 = new DeflateCompressorInputStream(pipedInputStream0);
      deflateCompressorInputStream0.close();
      assertEquals(0, deflateCompressorInputStream0.getCount());
  }