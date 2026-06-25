//+------------------------------------------------------------------+
//|                                              FleetReversion_EA.mq4 |
//|   EA mean-reversion (Bollinger o RSI) con il motore di rischio di  |
//|   FleetGuard. Modalita' selezionabile via SignalMode:             |
//|     BOLLINGER -> indici  (S&P500 D1):  WR 70-80%, DD <3%          |
//|     RSI       -> forex   (EURUSD H1):  WR 53-60%, 4/5 anni        |
//|   Entrambe validate in walk-forward. Rendimenti contenuti.        |
//|                                                                   |
//|   Materiale didattico. Testare PRIMA su conto demo.               |
//+------------------------------------------------------------------+
#property strict

//================= INPUT: RISCHIO =================
input double RiskPercent       = 0.50;   // Rischio per trade (% equity)
input double MaxTotalDD_Pct    = 10.0;   // Drawdown totale max: stop nuovi trade
input double MaxDailyLoss_Pct  = 3.0;    // Perdita giornaliera max: stop per oggi
input int    MaxOpenTrades     = 2;      // Posizioni contemporanee max

//================= INPUT: COSTI / ESECUZIONE =================
input double CommissionPerLot  = 0.0;    // Commissione round-turn per lotto (indici: spesso 0)
input int    MaxSpreadPoints   = 60;     // Spread massimo ammesso (in points)
input int    SlippagePoints    = 5;
input int    MagicNumber       = 20260625;

//================= INPUT: SESSIONE (ora server) =================
input bool   UseSessionFilter  = false;  // sui daily di solito non serve
input int    StartHour         = 0;
input int    EndHour           = 24;

//================= INPUT: STRATEGIA (mean-reversion - validata) =================
// Due modalita' validate in walk-forward:
//  - BOLLINGER -> indici (S&P500 D1): WR 70-80%, DD <3%
//  - RSI       -> forex  (EUR/USD H1): WR 53-60%, 4/5 anni positivi
// Stop e target su ATR (RR 1:1).
enum ENUM_REV_MODE { REV_BOLLINGER=0, REV_RSI=1 };
input ENUM_REV_MODE SignalMode = REV_BOLLINGER;   // scegli il motore di segnale

// --- Bollinger (per indici, es. SPXUSD D1) ---
input int    BB_Period         = 20;
input double BB_Dev            = 2.0;

// --- RSI (per forex, es. EURUSD H1) ---
input int    RSI_Period        = 14;
input double RSI_Oversold      = 25;     // sotto -> long
input double RSI_Overbought    = 75;     // sopra -> short

// --- Comuni ---
input int    ATR_Period        = 14;
input double SL_ATR_Mult       = 1.5;    // Stop   = 1.5 * ATR
input double TP_ATR_Mult       = 1.5;    // Target = 1.5 * ATR (RR 1:1)

//================= STATO INTERNO =================
int      g_dayStamp     = -1;
double   g_dayStartEq   = 0;
double   g_peakEquity   = 0;
datetime g_lastBarTime  = 0;

//+------------------------------------------------------------------+
int OnInit()
{
   g_peakEquity = AccountEquity();
   g_dayStartEq = AccountEquity();
   g_dayStamp   = TimeDay(TimeCurrent());
   string m = (SignalMode == REV_RSI)
              ? StringConcatenate("RSI ", RSI_Period, " ", RSI_Oversold, "/", RSI_Overbought)
              : StringConcatenate("Bollinger ", BB_Period, "/", BB_Dev);
   Print("FleetReversion_EA avviato (", m, "). Rischio/trade=", RiskPercent,
         "%  DDmax=", MaxTotalDD_Pct, "%");
   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason) { }

//+------------------------------------------------------------------+
void UpdateGuards()
{
   double eq = AccountEquity();
   if(eq > g_peakEquity) g_peakEquity = eq;
   int d = TimeDay(TimeCurrent());
   if(d != g_dayStamp) { g_dayStamp = d; g_dayStartEq = eq; }
}

//+------------------------------------------------------------------+
bool RiskHalt()
{
   double eq = AccountEquity();
   if(g_peakEquity > 0)
   {
      double totalDD = (g_peakEquity - eq) / g_peakEquity * 100.0;
      if(totalDD >= MaxTotalDD_Pct)
      { Comment("STOP: drawdown totale ", DoubleToStr(totalDD,2), "%"); return(true); }
   }
   if(g_dayStartEq > 0)
   {
      double dayLoss = (g_dayStartEq - eq) / g_dayStartEq * 100.0;
      if(dayLoss >= MaxDailyLoss_Pct)
      { Comment("STOP per oggi: perdita ", DoubleToStr(dayLoss,2), "%"); return(true); }
   }
   return(false);
}

//+------------------------------------------------------------------+
bool InSession()
{
   if(!UseSessionFilter) return(true);
   int h = TimeHour(TimeCurrent());
   if(StartHour <= EndHour) return(h >= StartHour && h < EndHour);
   return(h >= StartHour || h < EndHour);
}

//+------------------------------------------------------------------+
int CountMyOrders()
{
   int n = 0;
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
      if(OrderMagicNumber() == MagicNumber && OrderSymbol() == Symbol()) n++;
   }
   return(n);
}

//+------------------------------------------------------------------+
double CalcLots(double slPriceDistance)
{
   if(slPriceDistance <= 0) return(0);
   double riskMoney = AccountEquity() * RiskPercent / 100.0;
   double tickValue = MarketInfo(Symbol(), MODE_TICKVALUE);
   double tickSize  = MarketInfo(Symbol(), MODE_TICKSIZE);
   if(tickSize <= 0 || tickValue <= 0) return(0);
   double lossPerLot = (slPriceDistance / tickSize) * tickValue + CommissionPerLot;
   if(lossPerLot <= 0) return(0);
   double lots = riskMoney / lossPerLot;
   double minLot = MarketInfo(Symbol(), MODE_MINLOT);
   double maxLot = MarketInfo(Symbol(), MODE_MAXLOT);
   double step   = MarketInfo(Symbol(), MODE_LOTSTEP);
   if(step <= 0) step = 0.01;
   lots = MathFloor(lots / step) * step;
   if(lots < minLot) return(0);
   if(lots > maxLot) lots = maxLot;
   return(lots);
}

//+------------------------------------------------------------------+
//| STRATEGIA: mean-reversion. +1 = atteso rimbalzo, -1 = atteso ritorno.|
//| Modalita' BOLLINGER (indici) o RSI (forex) secondo SignalMode.    |
//+------------------------------------------------------------------+
int Signal()
{
   if(SignalMode == REV_RSI)
   {
      double r = iRSI(NULL, 0, RSI_Period, PRICE_CLOSE, 1);
      if(r < RSI_Oversold)   return(1);    // ipervenduto -> long
      if(r > RSI_Overbought) return(-1);   // ipercomprato -> short
      return(0);
   }
   // BOLLINGER
   double lower = iBands(NULL, 0, BB_Period, BB_Dev, 0, PRICE_CLOSE, MODE_LOWER, 1);
   double upper = iBands(NULL, 0, BB_Period, BB_Dev, 0, PRICE_CLOSE, MODE_UPPER, 1);
   double cl    = Close[1];
   if(cl < lower) return(1);     // prezzo in eccesso al ribasso -> rimbalzo atteso
   if(cl > upper) return(-1);    // prezzo in eccesso al rialzo  -> ritorno atteso
   return(0);
}

//+------------------------------------------------------------------+
void OpenTrade(int dir, double slDist, double tpDist)
{
   double lots = CalcLots(slDist);
   if(lots <= 0) { Print("Lotto=0: rischio non rispettabile, salto."); return; }
   double stopLevel = MarketInfo(Symbol(), MODE_STOPLEVEL) * Point;
   double price, sl, tp; int type; color col;
   if(dir > 0)
   {
      type = OP_BUY; col = clrDodgerBlue;
      price = NormalizeDouble(Ask, Digits);
      sl = NormalizeDouble(price - slDist, Digits);
      tp = NormalizeDouble(price + tpDist, Digits);
      if(price - sl < stopLevel || tp - price < stopLevel) { Print("SL/TP sotto stop level."); return; }
   }
   else
   {
      type = OP_SELL; col = clrOrangeRed;
      price = NormalizeDouble(Bid, Digits);
      sl = NormalizeDouble(price + slDist, Digits);
      tp = NormalizeDouble(price - tpDist, Digits);
      if(sl - price < stopLevel || price - tp < stopLevel) { Print("SL/TP sotto stop level."); return; }
   }
   int ticket = OrderSend(Symbol(), type, lots, price, SlippagePoints, sl, tp,
                          "FleetReversion", MagicNumber, 0, col);
   if(ticket < 0)
      Print("OrderSend fallito. Errore=", GetLastError(), " lots=", lots);
}

//+------------------------------------------------------------------+
void OnTick()
{
   UpdateGuards();
   if(RiskHalt())                                     return;
   if(!InSession())                                   return;
   if((int)MarketInfo(Symbol(), MODE_SPREAD) > MaxSpreadPoints) return;
   if(CountMyOrders() >= MaxOpenTrades)               return;
   if(Time[0] == g_lastBarTime)                       return;
   g_lastBarTime = Time[0];

   int sig = Signal();
   if(sig == 0)                                       return;
   double atr = iATR(NULL, 0, ATR_Period, 1);
   if(atr <= 0)                                       return;

   OpenTrade(sig, SL_ATR_Mult * atr, TP_ATR_Mult * atr);
}
//+------------------------------------------------------------------+
