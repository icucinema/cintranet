package uk.co.icucinema.ticketcollector;

import android.animation.Animator;
import android.animation.AnimatorListenerAdapter;
import android.annotation.TargetApi;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.database.DataSetObserver;
import android.nfc.NfcAdapter;
import android.nfc.Tag;
import android.nfc.tech.NfcA;
import android.os.AsyncTask;
import android.os.Build;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ListAdapter;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.TwoLineListItem;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;


public class WaitingForCardActivity extends ActionBarActivity {

    private ApiClient mApiClient;

    private NfcAdapter mAdapter;

    // Register for foreground NFC dispatch
    private PendingIntent mPendingIntent;
    private static final String[][] TECH_LISTS_ARRAY = new String[][] { new String[] {NfcA.class.getName()}};

    private ViewState mCurrentState;

    private TextView mPunterNameView;
    private TextView mPunterTicketCountView;
    private ListView mTicketsListView;

    private int mCurrentPunterId;
    private List<PointOfSaleService.Ticket> mTickets;

    private int mSelectedPrinterId;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_waiting_for_card);

        mApiClient = getIntent().getParcelableExtra("apiClient");
        mSelectedPrinterId = getIntent().getIntExtra("selectedPrinter", 1);
        mAdapter = NfcAdapter.getDefaultAdapter(this);

        mPendingIntent = PendingIntent.getActivity(
                this, 0, new Intent(this, getClass()).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP), 0);

        mCurrentState = ViewState.WAITING_FOR_CARD;

        mPunterNameView = (TextView)findViewById(R.id.lookup_punter_name);
        mPunterTicketCountView = (TextView)findViewById(R.id.lookup_punter_ticket_count);
        mTicketsListView = (ListView)findViewById(R.id.lookup_punter_tickets);

        Button collectPendingTicketsButton = (Button)findViewById(R.id.collect_pending_tickets_button);
        collectPendingTicketsButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                printWithStatus("pending_collection");
            }
        });

        transitionToState(ViewState.WAITING_FOR_CARD, true);
    }

    @Override
    protected void onResume() {
        super.onResume();
        mAdapter.enableForegroundDispatch(this, mPendingIntent, new IntentFilter[]{}, TECH_LISTS_ARRAY);
    }

    @Override
    protected void onPause() {
        super.onPause();
        mAdapter.disableForegroundDispatch(this);
    }

    /**
     * Shows the progress UI and hides the login form.
     */
    @TargetApi(Build.VERSION_CODES.HONEYCOMB_MR2)
    public void transitionToState(final ViewState show, boolean instant) {
        final View oldView = mCurrentState.thingToShow(this);
        final View newView = show.thingToShow(this);
        mCurrentState = show;

        if (oldView.equals(newView)) {
            // erk, what? - this probably means we're initializing
            for (View hideMe : show.thingsToHide(this)) {
                hideMe.setVisibility(View.GONE);
            }
            newView.setVisibility(View.VISIBLE);
            return;
        }

        // On Honeycomb MR2 we have the ViewPropertyAnimator APIs, which allow
        // for very easy animations. If available, use these APIs to fade-in
        // the progress spinner.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.HONEYCOMB_MR2 && !instant) {
            int shortAnimTime = getResources().getInteger(android.R.integer.config_shortAnimTime);

            oldView.setVisibility(View.GONE);
            oldView.animate().setDuration(shortAnimTime).alpha(
                    0).setListener(new AnimatorListenerAdapter() {
                @Override
                public void onAnimationEnd(Animator animation) {
                    oldView.setVisibility(View.GONE);
                }
            });

            newView.setVisibility(View.VISIBLE);
            newView.animate().setDuration(shortAnimTime).alpha(
                    1).setListener(new AnimatorListenerAdapter() {
                @Override
                public void onAnimationEnd(Animator animation) {
                    newView.setVisibility(View.VISIBLE);
                }
            });
        } else {
            // The ViewPropertyAnimator APIs are not available, so simply show
            // and hide the relevant UI components.
            oldView.setVisibility(View.GONE);
            newView.setVisibility(View.VISIBLE);
        }
    }

    // lazyweb
    // http://stackoverflow.com/questions/9655181/convert-from-byte-array-to-hex-string-in-java
    final private static char[] hexArray = "0123456789abcdef".toCharArray();
    private static String bytesToHex(byte[] bytes) {
        char[] hexChars = new char[bytes.length * 2];
        for ( int j = 0; j < bytes.length; j++ ) {
            int v = bytes[j] & 0xFF;
            hexChars[j * 2] = hexArray[v >>> 4];
            hexChars[j * 2 + 1] = hexArray[v & 0x0F];
        }
        return new String(hexChars);
    }

    @Override
    protected void onNewIntent(Intent intent) {
        Tag tagFromIntent = intent.getParcelableExtra(NfcAdapter.EXTRA_TAG);

        String hexId = bytesToHex(tagFromIntent.getId());

        System.out.print("Found tag: ");
        System.out.println(hexId);
        System.out.println(" !");

        new CardLookupTask().execute(hexId);
    }

    private void failedToGetPunter() {
        transitionToState(ViewState.WAITING_FOR_CARD, false);
    }

    private void gotPunter(PointOfSaleService.Punter punter) {
        System.out.println("Belonging to customer " + punter.getName() + "<" + punter.getId() + ">");

        if (punter.getName().trim().length() > 0) {
            mPunterNameView.setText(punter.getName());
        } else {
            mPunterNameView.setText("Unknown (ID: " + punter.getId() + ")");
        }

        mCurrentPunterId = punter.getId();
        new TicketLookupTask().execute(punter.getId());
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_waiting_for_card, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        return super.onOptionsItemSelected(item);
    }

    public class CardLookupTask extends AsyncTask<String, Void, List<PointOfSaleService.Punter>> {
        @Override
        protected List<PointOfSaleService.Punter> doInBackground(String... params) {
            String cardId = params[0];
            return mApiClient.getPosService().puntersByCard(cardId).getResults();
        }

        @Override
        protected void onPreExecute() {
            transitionToState(ViewState.LOOKING_UP_CARD, false);
        }

        @Override
        protected void onPostExecute(List<PointOfSaleService.Punter> punters) {
            if (punters.size() == 0) {
                Toast.makeText(WaitingForCardActivity.this, R.string.no_such_customer, Toast.LENGTH_SHORT).show();
                WaitingForCardActivity.this.failedToGetPunter();
                return;
            } else if (punters.size() > 1) {
                Toast.makeText(WaitingForCardActivity.this, R.string.multiple_results, Toast.LENGTH_SHORT).show();
                WaitingForCardActivity.this.failedToGetPunter();
                return;
            }

            WaitingForCardActivity.this.gotPunter(punters.get(0));
        }
    }

    public class TicketLookupTask extends AsyncTask<Integer, Void, List<PointOfSaleService.Ticket>> {
        @Override
        protected List<PointOfSaleService.Ticket> doInBackground(Integer... params) {
            int punterId = params[0];
            return mApiClient.getPosService().ticketsForPunter(punterId);
        }

        @Override
        protected void onPostExecute(List<PointOfSaleService.Ticket> tickets) {
            WaitingForCardActivity.this.gotTickets(tickets);
        }
    }

    public class PrintTicketsTask extends AsyncTask<PointOfSaleService.Ticket, Void, Void> {
        @Override
        protected Void doInBackground(PointOfSaleService.Ticket... tickets) {
            int[] ticketIds = new int[tickets.length];

            PointOfSaleService posService = mApiClient.getPosService();

            int n = 0;
            for (PointOfSaleService.Ticket ticket : tickets) {
                if (ticket.getStatus().equals("pending_collection")) {
                    // we need to collect this
                    posService.collectTicket(ticket.getId());
                }
                ticketIds[n++] = ticket.getId();
            }

            posService.printTickets(mSelectedPrinterId, ticketIds);

            return (Void)null;
        }

        @Override
        protected void onPostExecute(Void returnValue) {
            new TicketLookupTask().execute(mCurrentPunterId);
        }
    }

    private void gotTickets(final List<PointOfSaleService.Ticket> tickets) {
        mTickets = tickets;

        ListAdapter ticketsAdapter = new ListAdapter() {
            private LayoutInflater inflater;

            @Override
            public boolean areAllItemsEnabled() {
                return true;
            }

            @Override
            public boolean isEnabled(int position) {
                return true;
            }

            @Override
            public void registerDataSetObserver(DataSetObserver observer) {
                // this never changes
            }

            @Override
            public void unregisterDataSetObserver(DataSetObserver observer) {
                // this never changes
            }

            @Override
            public int getCount() {
                return tickets.size();
            }

            @Override
            public Object getItem(int position) {
                return tickets.get(0);
            }

            @Override
            public long getItemId(int position) {
                return tickets.get(0).getId();
            }

            @Override
            public boolean hasStableIds() {
                return true;
            }

            @Override
            public View getView(int position, View convertView, ViewGroup parent) {
                if (inflater == null) {
                    inflater = (LayoutInflater)WaitingForCardActivity.this.getSystemService(
                            Context.LAYOUT_INFLATER_SERVICE
                    );
                }
                if (convertView == null) {
                    convertView = inflater.inflate(android.R.layout.simple_list_item_2, null);
                }

                PointOfSaleService.Ticket ticket = tickets.get(position);

                TextView text1 = (TextView)convertView.findViewById(android.R.id.text1);
                TextView text2 = (TextView)convertView.findViewById(android.R.id.text2);

                text1.setText(ticket.getTicketType().getEvent().getName());
                text2.setText("(" + ticket.getStatus() + ") " + ticket.getTicketType().getName());

                return convertView;
            }

            @Override
            public int getItemViewType(int position) {
                return 0;
            }

            @Override
            public int getViewTypeCount() {
                return 1;
            }

            @Override
            public boolean isEmpty() {
                return tickets.size() == 0;
            }
        };

        int pendingTicketsCount = 0;
        for (PointOfSaleService.Ticket ticket : tickets) {
            if (ticket.getStatus().equals("pending_collection")) // TODO: this should be an enum
                pendingTicketsCount++;
        }

        mTicketsListView.setAdapter(ticketsAdapter);
        mPunterTicketCountView.setText(tickets.size() + " tickets (" + pendingTicketsCount + " pending)");

        transitionToState(ViewState.SHOWING_PUNTER, false);
    }

    public void printWithStatus(String status) { // TODO: ENUMS!!!
        transitionToState(ViewState.LOOKING_UP_CARD, false);
        List<PointOfSaleService.Ticket> filteredTickets = new ArrayList<>();

        if (status != null) {
            for (PointOfSaleService.Ticket ticket : mTickets) {
                if (ticket.getStatus().equals(status)) {
                    filteredTickets.add(ticket);
                }
            }
        } else {
            filteredTickets = mTickets;
        }

        new PrintTicketsTask().execute(filteredTickets.toArray(new PointOfSaleService.Ticket[]{}));
    }
    public void printTickets() {
        printWithStatus(null);
    }

    private enum ViewState {
        WAITING_FOR_CARD(R.id.lookup_help_layout),
        LOOKING_UP_CARD(R.id.lookup_progress),
        SHOWING_PUNTER(R.id.lookup_punter),
        PRINTING_TICKETS(R.id.lookup_progress),;

        private final int mDisplayId;

        ViewState(int displayThing) {
            mDisplayId = displayThing;
        }

        public List<View> thingsToHide(WaitingForCardActivity waitingForCardActivity) {
            Set<View> vSet = new HashSet<>();
            for (ViewState x : ViewState.values()) {
                vSet.add(waitingForCardActivity.findViewById(x.mDisplayId));
            }
            vSet.remove(waitingForCardActivity.findViewById(this.mDisplayId));

            List<View> vList = new ArrayList<>();
            vList.addAll(vSet);

            return vList;
        }

        public View thingToShow(WaitingForCardActivity waitingForCardActivity) {
            return waitingForCardActivity.findViewById(this.mDisplayId);
        }
    }
}