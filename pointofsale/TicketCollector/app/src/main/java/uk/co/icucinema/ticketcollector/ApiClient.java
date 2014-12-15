package uk.co.icucinema.ticketcollector;

import android.graphics.Point;
import android.os.Parcel;
import android.os.Parcelable;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import retrofit.RequestInterceptor;
import retrofit.RestAdapter;
import retrofit.converter.GsonConverter;

public class ApiClient implements Parcelable {
    private String mApiUrl;

    private String mApiToken;

    private PointOfSaleService mPosService;

    public ApiClient(String apiUrl) {
        this(apiUrl, "");
    }
    public ApiClient(Parcel source) {
        this(source.readString(), source.readString());
    }
    public ApiClient(String apiUrl, String apiToken) {
        mApiUrl = apiUrl;
        mApiToken = apiToken;
        mPosService = buildPointOfSaleService(mApiToken);
    }

    private String buildUri(String path) {
        String url = mApiUrl;
        if (!url.endsWith("/")) {
            url += "/";
        }
        if (path.startsWith("/")) {
            path = path.substring(1);
        }
        if (!path.endsWith("/")) {
            path += "/";
        }

        return url + path;
    }

    public void login(String username, String password) {
        PointOfSaleService.TokenAuthResponse tar = mPosService.authenticate(username, password);
        mApiToken = tar.getAuthToken();

        mPosService = buildPointOfSaleService(mApiToken);
    }

    public PointOfSaleService getPosService() {
        return mPosService;
    }

    @Override
    public int describeContents() {
        return 0;
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeString(mApiUrl);
        dest.writeString(mApiToken);
    }

    public static final Parcelable.Creator<ApiClient> CREATOR = new Creator<ApiClient>() {
        @Override
        public ApiClient createFromParcel(Parcel source) {
            return new ApiClient(source);
        }

        @Override
        public ApiClient[] newArray(int size) {
            return new ApiClient[size];
        }
    };

    private PointOfSaleService buildPointOfSaleService(String apiToken) {
        Gson gson = new GsonBuilder().setDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'").create();

        RestAdapter restAdapter = new RestAdapter.Builder()
                .setLogLevel(RestAdapter.LogLevel.FULL)
                .setEndpoint(mApiUrl)
                .setConverter(new GsonConverter(gson))
                .setRequestInterceptor(buildRequestInterceptor(apiToken))
                .build();
        return restAdapter.create(PointOfSaleService.class);
    }

    private RequestInterceptor buildRequestInterceptor(final String apiToken) {
        return new RequestInterceptor() {
            @Override
            public void intercept(RequestFacade request) {
                if (apiToken != null && !apiToken.equals("")) {
                    request.addHeader("Authorization", "Token " + apiToken);
                }
            }
        };
    }
}
