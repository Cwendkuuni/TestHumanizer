package geo.google.mapping;

import geo.google.datamodel.*;
import geo.google.*;
import org.apache.commons.collections.*;
import oasis.names.tc.ciq.xsdschema.xal._2.*;
import java.util.*;

public final class AddressToUsAddressFunctor implements Functor<GeoUsAddress, GeoAddress, GeoException>
{
    private static final AddressToUsAddressFunctor _instance;
    
    public static AddressToUsAddressFunctor getInstance() {
        return AddressToUsAddressFunctor._instance;
    }
    
    @Override
    public GeoUsAddress execute(final GeoAddress addr) {
        final GeoUsAddress ret = new GeoUsAddress();
        final AddressDetails.Country country = addr.getAddressDetails().getCountry();
        if (country != null) {
            final List<AddressDetails.Country.CountryNameCode> countryNames = country.getCountryNameCode();
            if (CollectionUtils.isNotEmpty((Collection)countryNames)) {
                ret.setCountry(countryNames.get(0).getContent());
            }
            final AdministrativeArea adminArea = country.getAdministrativeArea();
            if (adminArea != null) {
                final List<AdministrativeArea.AdministrativeAreaName> names = adminArea.getAdministrativeAreaName();
                if (CollectionUtils.isNotEmpty((Collection)names)) {
                    ret.setState(names.get(0).getContent());
                }
                final AdministrativeArea.SubAdministrativeArea subAdminArea = adminArea.getSubAdministrativeArea();
                final Locality locality = (subAdminArea == null) ? adminArea.getLocality() : subAdminArea.getLocality();
                if (subAdminArea != null) {
                    final List<AdministrativeArea.SubAdministrativeArea.SubAdministrativeAreaName> subNames = subAdminArea.getSubAdministrativeAreaName();
                    if (CollectionUtils.isNotEmpty((Collection)subNames)) {
                        ret.setCounty(subNames.get(0).getContent());
                    }
                }
                if (locality != null) {
                    final List<Locality.LocalityName> localNames = locality.getLocalityName();
                    if (CollectionUtils.isNotEmpty((Collection)localNames)) {
                        ret.setCity(localNames.get(0).getContent());
                    }
                    final PostalCode postalCode = locality.getPostalCode();
                    final List<PostalCode.PostalCodeNumber> numbers = postalCode.getPostalCodeNumber();
                    if (CollectionUtils.isNotEmpty((Collection)numbers)) {
                        ret.setPostalCode(numbers.get(0).getContent());
                    }
                    if (locality.getThoroughfare() != null) {
                        final List<ThoroughfareNameType> thoroughfares = locality.getThoroughfare().getThoroughfareName();
                        if (CollectionUtils.isNotEmpty((Collection)thoroughfares)) {
                            ret.setAddressLine1(thoroughfares.get(0).getContent());
                            if (thoroughfares.size() > 1) {
                                ret.setAddressLine2(thoroughfares.get(1).getContent());
                            }
                        }
                    }
                }
            }
        }
        if (addr.getCoordinate() != null) {
            ret.setCoordinate(addr.getCoordinate().clone());
        }
        ret.setAccuracy(addr.getAccuracy());
        return ret;
    }
    
    static {
        _instance = new AddressToUsAddressFunctor();
    }
}
