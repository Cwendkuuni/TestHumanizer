@Test(timeout = 4000)
  public void test00()  throws Throwable  {
      CSVFormat cSVFormat0 = CSVFormat.TDF;
      CSVParser cSVParser0 = CSVParser.parse(")j", cSVFormat0);
      Iterator<CSVRecord> iterator0 = cSVParser0.iterator();
      assertNotNull(iterator0);
  }

  @Test(timeout = 4000)
  public void test01()  throws Throwable  {
      CSVFormat cSVFormat0 = CSVFormat.TDF;
      StringReader stringReader0 = new StringReader(") invalid char between encapsulated token and delimiter");
      CSVParser cSVParser0 = cSVFormat0.parse(stringReader0);
      boolean boolean0 = cSVParser0.isClosed();
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test02()  throws Throwable  {
      CSVFormat cSVFormat0 = CSVFormat.RFC4180;
      StringReader stringReader0 = new StringReader(")j");
      CSVParser cSVParser0 = cSVFormat0.parse(stringReader0);
      LinkedList<CSVRecord> linkedList0 = new LinkedList<CSVRecord>();
      cSVParser0.getRecords(linkedList0);
      assertEquals(1, linkedList0.size());
  }

  @Test(timeout = 4000)
  public void test03()  throws Throwable  {
      CSVFormat cSVFormat0 = CSVFormat.TDF;
      StringReader stringReader0 = new StringReader(") invalid char between encapsulated token and delimiter");
      CSVParser cSVParser0 = cSVFormat0.parse(stringReader0);
      CSVParser cSVParser1 = new CSVParser(stringReader0, cSVFormat0);
      cSVParser1.close();
      Consumer<Object> consumer0 = (Consumer<Object>) mock(Consumer.class, new ViolatedAssumptionAnswer());
      // Undeclared exception!
      try { 
        cSVParser0.forEach(consumer0);
        fail("Expecting exception: RuntimeException");
      
      } catch(RuntimeException e) {
         //
         // java.io.IOException: Stream closed
         //
         verifyException("org.apache.commons.csv.CSVParser$1", e);
      }
  }

  @Test(timeout = 4000)
  public void test04()  throws Throwable  {
      URLStreamHandler uRLStreamHandler0 = mock(URLStreamHandler.class, new ViolatedAssumptionAnswer());
      URL uRL0 = MockURL.URL("", "", 10, "", uRLStreamHandler0);
      Charset charset0 = Charset.defaultCharset();
      CSVFormat cSVFormat0 = CSVFormat.DEFAULT;
      // Undeclared exception!
      try { 
        CSVParser.parse(uRL0, charset0, cSVFormat0);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("java.net.URL", e);
      }
  }

  @Test(timeout = 4000)
  public void test05()  throws Throwable  {
      CSVFormat cSVFormat0 = CSVFormat.EXCEL;
      Character character0 = Character.valueOf('5');
      CSVFormat cSVFormat1 = cSVFormat0.withCommentStart(character0);
      CSVParser cSVParser0 = CSVParser.parse("5^<I", cSVFormat1);
      Consumer<Object> consumer0 = (Consumer<Object>) mock(Consumer.class, new ViolatedAssumptionAnswer());
      cSVParser0.forEach(consumer0);
      assertEquals(0L, cSVParser0.getRecordNumber());
  }

  @Test(timeout = 4000)
  public void test06()  throws Throwable  {
      CSVFormat cSVFormat0 = CSVFormat.TDF;
      CSVParser cSVParser0 = CSVParser.parse("Delimiter=<\t> Escape=<L> QuoteChar=<\"> RecordSeparator=<\r\n> EmptyLines:ignored SurroundingSpaces:ignored SkipHeaderRecord:false", cSVFormat0);
      CSVRecord cSVRecord0 = cSVParser0.nextRecord();
      assertEquals("[Delimiter=<, > Escape=<L> QuoteChar=<\"> RecordSeparator=<]", cSVRecord0.toString());
  }

  @Test(timeout = 4000)
  public void test07()  throws Throwable  {
      CSVFormat cSVFormat0 = CSVFormat.DEFAULT;
      CSVParser cSVParser0 = CSVParser.parse("8m>$`ftxi^,lu", cSVFormat0);
      cSVParser0.close();
      Consumer<Object> consumer0 = (Consumer<Object>) mock(Consumer.class, new ViolatedAssumptionAnswer());
      cSVParser0.forEach(consumer0);
      assertEquals(0L, cSVParser0.getRecordNumber());
  }

  @Test(timeout = 4000)
  public void test08()  throws Throwable  {
      CSVFormat cSVFormat0 = CSVFormat.EXCEL;
      String[] stringArray0 = new String[1];
      CSVFormat cSVFormat1 = cSVFormat0.withHeader(stringArray0);
      CSVFormat cSVFormat2 = cSVFormat1.withSkipHeaderRecord(true);
      StringReader stringReader0 = new StringReader("BK7.");
      CSVParser cSVParser0 = cSVFormat2.parse(stringReader0);
      assertEquals(1L, cSVParser0.getRecordNumber());
  }

  @Test(timeout = 4000)
  public void test09()  throws Throwable  {
      StringReader stringReader0 = new StringReader("8m>$`FtXi^,LU");
      CSVFormat cSVFormat0 = CSVFormat.EXCEL;
      String[] stringArray0 = new String[0];
      CSVFormat cSVFormat1 = cSVFormat0.withHeader(stringArray0);
      CSVParser cSVParser0 = cSVFormat1.parse(stringReader0);
      assertEquals(1L, cSVParser0.getRecordNumber());
      
      CSVParser cSVParser1 = cSVFormat1.parse(stringReader0);
      assertEquals(0L, cSVParser1.getRecordNumber());
  }

  @Test(timeout = 4000)
  public void test10()  throws Throwable  {
      CSVFormat cSVFormat0 = CSVFormat.TDF;
      StringReader stringReader0 = new StringReader("RQ");
      CSVParser cSVParser0 = cSVFormat0.parse(stringReader0);
      Map<String, Integer> map0 = cSVParser0.getHeaderMap();
      assertNull(map0);
  }

  @Test(timeout = 4000)
  public void test11()  throws Throwable  {
      CSVFormat cSVFormat0 = CSVFormat.TDF;
      StringReader stringReader0 = new StringReader(") invalid char between encapsulated token and delimiter");
      String[] stringArray0 = new String[1];
      CSVFormat cSVFormat1 = cSVFormat0.withHeader(stringArray0);
      CSVParser cSVParser0 = cSVFormat1.parse(stringReader0);
      Map<String, Integer> map0 = cSVParser0.getHeaderMap();
      assertNotNull(map0);
      assertEquals(1, map0.size());
      assertEquals(0L, cSVParser0.getRecordNumber());
  }

  @Test(timeout = 4000)
  public void test12()  throws Throwable  {
      CSVFormat cSVFormat0 = CSVFormat.TDF;
      CSVFormat cSVFormat1 = cSVFormat0.withNullString("-JIu*[AMclZ?J/x {");
      CSVParser cSVParser0 = CSVParser.parse("lwt<3AM 7", cSVFormat1);
      cSVParser0.nextRecord();
      assertEquals(1L, cSVParser0.getRecordNumber());
  }

  @Test(timeout = 4000)
  public void test13()  throws Throwable  {
      CSVFormat cSVFormat0 = CSVFormat.RFC4180;
      CSVFormat cSVFormat1 = cSVFormat0.withNullString("p5[N[");
      CSVParser cSVParser0 = CSVParser.parse("p5[N[", cSVFormat1);
      cSVParser0.nextRecord();
      assertEquals(1L, cSVParser0.getRecordNumber());
  }

  @Test(timeout = 4000)
  public void test14()  throws Throwable  {
      CSVFormat cSVFormat0 = CSVFormat.RFC4180;
      StringReader stringReader0 = new StringReader(")j");
      CSVParser cSVParser0 = cSVFormat0.parse(stringReader0);
      long long0 = cSVParser0.getRecordNumber();
      assertEquals(0L, long0);
  }

  @Test(timeout = 4000)
  public void test15()  throws Throwable  {
      CSVFormat cSVFormat0 = CSVFormat.TDF;
      StringReader stringReader0 = new StringReader("2");
      CSVParser cSVParser0 = cSVFormat0.parse(stringReader0);
      long long0 = cSVParser0.getCurrentLineNumber();
      assertEquals(0L, long0);
  }

  @Test(timeout = 4000)
  public void test16()  throws Throwable  {
      CSVFormat cSVFormat0 = CSVFormat.RFC4180;
      File file0 = MockFile.createTempFile("vK<spap[61", "vK<spap[61");
      CSVParser cSVParser0 = CSVParser.parse(file0, cSVFormat0);
      assertEquals(0L, cSVParser0.getRecordNumber());
  }

  @Test(timeout = 4000)
  public void test17()  throws Throwable  {
      CSVFormat cSVFormat0 = CSVFormat.DEFAULT;
      CSVParser cSVParser0 = CSVParser.parse("-xG)#cSAstvioF}y(*:", cSVFormat0);
      cSVParser0.getRecords();
      assertEquals(1L, cSVParser0.getRecordNumber());
  }

  @Test(timeout = 4000)
  public void test18()  throws Throwable  {
      CSVFormat cSVFormat0 = CSVFormat.TDF;
      StringReader stringReader0 = new StringReader(") invalid char between encapsulated token and delimiter");
      CSVParser cSVParser0 = cSVFormat0.parse(stringReader0);
      Consumer<Object> consumer0 = (Consumer<Object>) mock(Consumer.class, new ViolatedAssumptionAnswer());
      cSVParser0.forEach(consumer0);
      assertEquals(1L, cSVParser0.getRecordNumber());
  }