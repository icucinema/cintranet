package uk.co.icucinema.ticketcollector;

import com.google.gson.annotations.SerializedName;

import java.util.Date;
import java.util.List;

import retrofit.http.Field;
import retrofit.http.FormUrlEncoded;
import retrofit.http.GET;
import retrofit.http.POST;
import retrofit.http.Path;
import retrofit.http.Query;

public interface PointOfSaleService {
    @POST("/api-token-auth/")
    @FormUrlEncoded
    public TokenAuthResponse authenticate(@Field("username") String username, @Field("password") String password);

    @GET("/punters/")
    public ListResponse<Punter> puntersByCard(@Query("card_id") String cardId);

    @GET("/punters/{punter_id}/tickets/?detailed=true")
    public List<Ticket> ticketsForPunter(@Path("punter_id") int punterId);

    @GET("/punters/{punter_id}/tickets/?detailed=true")
    public List<Ticket> ticketsForPunter(@Path("punter_id") int punterId, @Query("status") String status);

    @POST("/tickets/{ticket_id}/collect/")
    public Object collectTicket(@Path("ticket_id") int ticketId);

    @POST("/printers/{printer_id}/print_tickets/")
    @FormUrlEncoded
    public Object printTickets(@Path("printer_id") int printerId, @Field("tickets") int[] ticketIds);

    @GET("/printers/")
    public ListResponse<Printer> printers();

    public class Printer {
        @SerializedName("id")
        private int id;

        @SerializedName("name")
        private String name;

        @SerializedName("last_seen")
        private Date lastSeen;

        public int getId() {
            return id;
        }

        public String getName() {
            return name;
        }

        public Date getLastSeen() {
            return lastSeen;
        }

        @Override
        public String toString() {
            return name + " (" + id + ")";
        }
    }

    public class Event {
        @SerializedName("id")
        private int id;

        @SerializedName("name")
        private String name;

        @SerializedName("start_time")
        private Date startTime;

        public int getId() {
            return id;
        }

        public String getName() {
            return name;
        }

        public Date getStartTime() {
            return startTime;
        }
    }
    public class Ticket {
        @SerializedName("id")
        private int id;

        @SerializedName("status")
        private String status;

        @SerializedName("timestamp")
        private Date timestamp;

        @SerializedName("ticket_type")
        private TicketType ticketType;

        public int getId() {
            return id;
        }

        public String getStatus() {
            return status;
        }

        public Date getTimestamp() {
            return timestamp;
        }

        public TicketType getTicketType() {
            return ticketType;
        }

        public class TicketType {
            @SerializedName("id")
            private int id;

            @SerializedName("name")
            private String name;

            @SerializedName("sale_price")
            private String salePrice;

            @SerializedName("event")
            private Event event;

            public int getId() {
                return id;
            }

            public String getName() {
                return name;
            }

            public String getSalePrice() {
                return salePrice;
            }

            public Event getEvent() {
                return event;
            }
        }
    }

    public class Punter {
        @SerializedName("id")
        private int id;

        @SerializedName("name")
        private String name;

        public int getId() {
            return id;
        }

        public String getName() {
            return name;
        }
    }

    public class ListResponse<T> {
        @SerializedName("results")
        private List<T> results;

        public List<T> getResults() {
            return results;
        }
    }

    public class TokenAuthResponse {
        @SerializedName("token")
        private String mAuthToken;

        public String getAuthToken() {
            return mAuthToken;
        }
    }
}
