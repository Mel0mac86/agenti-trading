//+------------------------------------------------------------------+
//|                                                  FleetGuard_EA.mq4 |
//|   Motore EA "risk-first" e cost-aware per MetaTrader 4.           |
//|   La logica di rischio (DD, perdita giornaliera, spread,          |
//|   commissioni, sizing) e' separata dalla strategia, che e'        |
//|   agganciabile nella funzione Signal().                           |
//|                                                                   |
//|   Materiale didattico. Il trading comporta rischio di perdita.    |
//|   Testare PRIMA su conto demo con lo Strategy Tester.             |
//+------------------------------------------------------------------+
#property strict

//================= INPUT: RISCHIO =================
input double RiskPercent       = 0.75;   // Rischio per trade (% equity)
input double MaxTotalDD_Pct    = 10.0;   // Drawdown totale max: stop nuovi trade
input double MaxDailyLoss_Pct  = 3.0;    // Perdita giornaliera max: stop per oggi
input int    MaxOpenTrades     = 2;      // Posizioni contemporanee max (questo EA)
input double MinRR             = 1.5;    // R:R minimo per accettare un trade

//================= INPUT: COSTI / ESECUZIONE =================
input double CommissionPerLot  = 7.0;    // Commissione round-turn per lotto (valuta conto)
input int    MaxSpreadPoints   = 35;     // Spread massimo ammesso (in points)
input int    SlippagePoints    = 5;      // Slippage massimo
input int    MagicNumber       = 20260624;

//================= INPUT: SESSIONE (ora server) =================
input bool   UseSessionFilter  = true;
input int    StartHour         = 7;      // inclusa
input int    EndHour           = 20;     // esclusa

//================= INPUT: STRATEGIA ESEMPIO (trend + ATR) =================
// Placeholder sostituibile: trend-following EMA con stop/target su ATR.
input int    FastMA            = 20;
input int    SlowMA            = 50;
input int    ATR_Period        = 14;
input double SL_ATR_Mult       = 2.0;    // Stop  = SL_ATR_Mult * ATR
input double TP_ATR_Mult       = 3.0;    // Target= TP_ATR_Mult * ATR

//================= STATO INTERNO =================
int      g_dayStamp     = -1;     // giorno corrente (1..31) per il reset giornaliero
double   g_dayStartEq   = 0;      // equity a inizio giornata
double   g_peakEquity   = 0;      // massimo equity storico (per il DD)
datetime g_lastBarTime  = 0;      // per operare una volta per barra

//+------------------------------------------------------------------+
int OnInit()
{
   g_peakEquity = AccountEquity();
   g_dayStartEq = AccountEquity();
   g_dayStamp   = TimeDay(TimeCurrent());
   Print("FleetGuard_EA avviato. Rischio/trade=", RiskPercent,
         "%  DDmax=", MaxTotalDD_Pct, "%  PerditaGiorn.max=", MaxDailyLoss_Pct, "%");
   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason) { }

//+------------------------------------------------------------------+
//| Aggiorna picco equity e reset giornaliero                        |
//+------------------------------------------------------------------+
void UpdateGuards()
{
   double eq = AccountEquity();
   if(eq > g_peakEquity) g_peakEquity = eq;

   int d = TimeDay(TimeCurrent());
   if(d != g_dayStamp)
   {
      g_dayStamp   = d;
      g_dayStartEq = eq;   // nuova giornata: azzera il contatore di perdita
   }
}

//+------------------------------------------------------------------+
//| True se una guardia di rischio impone di NON aprire nuovi trade  |
//+------------------------------------------------------------------+
bool RiskHalt()
{
   double eq = AccountEquity();

   if(g_peakEquity > 0)
   {
      double totalDD = (g_peakEquity - eq) / g_peakEquity * 100.0;
      if(totalDD >= MaxTotalDD_Pct)
      {
         Comment("STOP: drawdown totale ", DoubleToStr(totalDD,2), "% >= ", MaxTotalDD_Pct, "%");
         return(true);
      }
   }
   if(g_dayStartEq > 0)
   {
      double dayLoss = (g_dayStartEq - eq) / g_dayStartEq * 100.0;
      if(dayLoss >= MaxDailyLoss_Pct)
      {
         Comment("STOP per oggi: perdita giornaliera ", DoubleToStr(dayLoss,2), "%");
         return(true);
      }
   }
   return(false);
}

//+------------------------------------------------------------------+
//| Filtro orario di sessione                                        |
//+------------------------------------------------------------------+
bool InSession()
{
   if(!UseSessionFilter) return(true);
   int h = TimeHour(TimeCurrent());
   if(StartHour <= EndHour) return(h >= StartHour && h < EndHour);
   // sessione a cavallo della mezzanotte
   return(h >= StartHour || h < EndHour);
}

//+------------------------------------------------------------------+
//| Conta gli ordini aperti da questo EA su questo simbolo           |
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
//| Sizing del lotto: rischio % equity / (perdita allo stop + comm.) |
//| Include la commissione nel rischio. Se non rispettabile -> 0.    |
//+------------------------------------------------------------------+
double CalcLots(double slPriceDistance)
{
   if(slPriceDistance <= 0) return(0);

   double riskMoney = AccountEquity() * RiskPercent / 100.0;
   double tickValue = MarketInfo(Symbol(), MODE_TICKVALUE);
   double tickSize  = MarketInfo(Symbol(), MODE_TICKSIZE);
   if(tickSize <= 0 || tickValue <= 0) return(0);

   // perdita per 1 lotto = (distanza/tick) * valore tick + commissione round-turn
   double lossPerLot = (slPriceDistance / tickSize) * tickValue + CommissionPerLot;
   if(lossPerLot <= 0) return(0);

   double lots = riskMoney / lossPerLot;

   double minLot = MarketInfo(Symbol(), MODE_MINLOT);
   double maxLot = MarketInfo(Symbol(), MODE_MAXLOT);
   double step   = MarketInfo(Symbol(), MODE_LOTSTEP);
   if(step <= 0) step = 0.01;

   lots = MathFloor(lots / step) * step;   // arrotonda PER DIFETTO: mai eccedere il rischio
   if(lots < minLot) return(0);             // troppo piccolo: meglio non tradare
   if(lots > maxLot) lots = maxLot;
   return(lots);
}

//+------------------------------------------------------------------+
//| STRATEGIA (placeholder): incrocio EMA. +1 long, -1 short, 0 nulla|
//| Sostituibile con la logica decisa dal backtest (misto).          |
//+------------------------------------------------------------------+
int Signal()
{
   double fastNow  = iMA(NULL, 0, FastMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double slowNow  = iMA(NULL, 0, SlowMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double fastPrev = iMA(NULL, 0, FastMA, 0, MODE_EMA, PRICE_CLOSE, 2);
   double slowPrev = iMA(NULL, 0, SlowMA, 0, MODE_EMA, PRICE_CLOSE, 2);

   if(fastPrev <= slowPrev && fastNow > slowNow) return(1);   // incrocio rialzista
   if(fastPrev >= slowPrev && fastNow < slowNow) return(-1);  // incrocio ribassista
   return(0);
}

//+------------------------------------------------------------------+
//| Apertura ordine con SL/TP normalizzati e rispetto stop level     |
//+------------------------------------------------------------------+
void OpenTrade(int dir, double slDist, double tpDist)
{
   double lots = CalcLots(slDist);
   if(lots <= 0) { Print("Lotto=0: rischio non rispettabile, salto il trade."); return; }

   double stopLevel = MarketInfo(Symbol(), MODE_STOPLEVEL) * Point;
   double price, sl, tp;
   int    type;
   color  col;

   if(dir > 0)
   {
      type  = OP_BUY;  col = clrDodgerBlue;
      price = NormalizeDouble(Ask, Digits);
      sl    = NormalizeDouble(price - slDist, Digits);
      tp    = NormalizeDouble(price + tpDist, Digits);
      if(price - sl < stopLevel || tp - price < stopLevel) { Print("SL/TP sotto stop level, salto."); return; }
   }
   else
   {
      type  = OP_SELL; col = clrOrangeRed;
      price = NormalizeDouble(Bid, Digits);
      sl    = NormalizeDouble(price + slDist, Digits);
      tp    = NormalizeDouble(price - tpDist, Digits);
      if(sl - price < stopLevel || price - tp < stopLevel) { Print("SL/TP sotto stop level, salto."); return; }
   }

   int ticket = OrderSend(Symbol(), type, lots, price, SlippagePoints, sl, tp,
                          "FleetGuard", MagicNumber, 0, col);
   if(ticket < 0)
      Print("OrderSend fallito. Errore=", GetLastError(),
            "  lots=", lots, " price=", price, " sl=", sl, " tp=", tp);
}

//+------------------------------------------------------------------+
void OnTick()
{
   UpdateGuards();

   // 1) guardie di rischio: bloccano nuovi ingressi
   if(RiskHalt())                                     return;
   // 2) filtro sessione
   if(!InSession())                                   return;
   // 3) filtro spread (costo d'ingresso)
   if((int)MarketInfo(Symbol(), MODE_SPREAD) > MaxSpreadPoints) return;
   // 4) limite posizioni contemporanee
   if(CountMyOrders() >= MaxOpenTrades)               return;

   // 5) una valutazione per barra (niente overtrading, niente ripittura)
   if(Time[0] == g_lastBarTime)                       return;
   g_lastBarTime = Time[0];

   int sig = Signal();
   if(sig == 0)                                       return;

   double atr = iATR(NULL, 0, ATR_Period, 1);
   if(atr <= 0)                                       return;

   double slDist = SL_ATR_Mult * atr;
   double tpDist = TP_ATR_Mult * atr;

   // R:R minimo (lo spread reale e' gia' filtrato sopra)
   if(slDist <= 0 || (tpDist / slDist) < MinRR)       return;

   OpenTrade(sig, slDist, tpDist);
}
//+------------------------------------------------------------------+
