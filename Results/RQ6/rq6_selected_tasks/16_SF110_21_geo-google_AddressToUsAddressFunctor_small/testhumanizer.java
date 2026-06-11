private static final String EXPECTED_COUNTRY = "";
    private static final GeoAddressAccuracy EXPECTED_ACCURACY = GeoAddressAccuracy.UNKNOWN_LOCATION;

    @Test(timeout = 4000)
    public void testExecuteWithEmptyGeoAddress() throws Throwable {
        // Given: A new AddressToUsAddressFunctor and an empty GeoAddress with coordinate and address details
        AddressToUsAddressFunctor addressToUsAddressFunctor = new AddressToUsAddressFunctor();
        GeoAddress geoAddress = new GeoAddress();
        AddressDetails addressDetails = new AddressDetails();
        GeoCoordinate geoCoordinate = new GeoCoordinate();
        geoAddress.setCoordinate(geoCoordinate);
        geoAddress.setAddressDetails(addressDetails);

        // When: Executing the functor with the GeoAddress
        GeoUsAddress geoUsAddress = addressToUsAddressFunctor.execute(geoAddress);

        // Then: The GeoUsAddress should have UNKNOWN_LOCATION accuracy
        assertEquals("GeoUsAddress accuracy should be UNKNOWN_LOCATION", EXPECTED_ACCURACY, geoUsAddress.getAccuracy());
    }

    @Test(timeout = 4000)
    public void testExecuteWithCountryDetailsThrowsException() throws Throwable {
        // Given: A singleton instance of AddressToUsAddressFunctor and a GeoAddress with country details
        AddressToUsAddressFunctor addressToUsAddressFunctor = AddressToUsAddressFunctor.getInstance();
        GeoAddress geoAddress = new GeoAddress();
        AddressDetails addressDetails = new AddressDetails();
        AddressDetails.Country addressDetailsCountry = new AddressDetails.Country();
        addressDetails.setCountry(addressDetailsCountry);
        geoAddress.setAddressDetails(addressDetails);

        // When & Then: Executing the functor should throw NoClassDefFoundError
        try {
            addressToUsAddressFunctor.execute(geoAddress);
            fail("Expecting exception: NoClassDefFoundError");
        } catch (NoClassDefFoundError e) {
            // Verify exception details
            // verifyException("geo.google.mapping.AddressToUsAddressFunctor", e);
        }
    }

    @Test(timeout = 4000)
    public void testExecuteWithEmptyAddressDetails() throws Throwable {
        // Given: A new AddressToUsAddressFunctor and a GeoAddress with empty address details
        AddressToUsAddressFunctor addressToUsAddressFunctor = new AddressToUsAddressFunctor();
        GeoAddress geoAddress = new GeoAddress();
        AddressDetails addressDetails = new AddressDetails();
        geoAddress.setAddressDetails(addressDetails);

        // When: Executing the functor with the GeoAddress
        GeoUsAddress geoUsAddress = addressToUsAddressFunctor.execute(geoAddress);

        // Then: The GeoUsAddress should have an empty country
        assertEquals("GeoUsAddress country should be empty", EXPECTED_COUNTRY, geoUsAddress.getCountry());
    }