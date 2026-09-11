// ============================================================================
// FALCON AIR NETWORK ANALYTICS — POWER QUERY (M) TRANSFORMATION LAYER
// ============================================================================

// ----------------------------------------------------------------------------
// QUERY 1: Dim_Date  (fully dynamic, parameter-driven date table)
// Create as a Blank Query named "Dim_Date"
// ----------------------------------------------------------------------------
let
    StartDate = #date(2025, 1, 1),
    EndDate   = #date(2025, 12, 31),
    FiscalYearStartMonth = 4,   // Airline FY starts April 1 — change if needed

    DayCount = Duration.Days(EndDate - StartDate) + 1,
    DateList = List.Dates(StartDate, DayCount, #duration(1, 0, 0, 0)),
    #"Converted to Table" = Table.FromList(DateList, Splitter.SplitByNothing(), {"Date"}),
    #"Changed Type" = Table.TransformColumnTypes(#"Converted to Table", {{"Date", type date}}),

    #"Added DateKey" = Table.AddColumn(#"Changed Type", "DateKey",
        each Date.Year([Date]) * 10000 + Date.Month([Date]) * 100 + Date.Day([Date]), Int64.Type),

    #"Added Year" = Table.AddColumn(#"Added DateKey", "Year", each Date.Year([Date]), Int64.Type),
    #"Added Month" = Table.AddColumn(#"Added Year", "Month", each Date.Month([Date]), Int64.Type),
    #"Added MonthName" = Table.AddColumn(#"Added Month", "MonthName", each Date.ToText([Date], "MMMM"), type text),
    #"Added MonthShort" = Table.AddColumn(#"Added MonthName", "MonthShortName", each Date.ToText([Date], "MMM"), type text),
    #"Added MonthSortIndex" = Table.AddColumn(#"Added MonthShort", "MonthSortIndex",
        each [Year] * 100 + [Month], Int64.Type),

    #"Added Quarter" = Table.AddColumn(#"Added MonthSortIndex", "Quarter",
        each "Q" & Number.ToText(Date.QuarterOfYear([Date])), type text),
    #"Added QuarterSortIndex" = Table.AddColumn(#"Added Quarter", "QuarterSortIndex",
        each [Year] * 10 + Date.QuarterOfYear([Date]), Int64.Type),

    // Fiscal calendar (shifted by FiscalYearStartMonth)
    #"Added FiscalMonth" = Table.AddColumn(#"Added QuarterSortIndex", "FiscalMonth",
        each Number.Mod([Month] - FiscalYearStartMonth, 12) + 1, Int64.Type),
    #"Added FiscalQuarter" = Table.AddColumn(#"Added FiscalMonth", "FiscalQuarter",
        each "FQ" & Number.ToText(Number.RoundUp([FiscalMonth] / 3)), type text),
    #"Added FiscalYear" = Table.AddColumn(#"Added FiscalQuarter", "FiscalYear",
        each if [Month] >= FiscalYearStartMonth then [Year] + 1 else [Year], Int64.Type),

    #"Added WeekNumber" = Table.AddColumn(#"Added FiscalYear", "WeekNumber", each Date.WeekOfYear([Date]), Int64.Type),
    #"Added DayOfWeek" = Table.AddColumn(#"Added WeekNumber", "DayOfWeekNumber",
        each Date.DayOfWeek([Date], Day.Monday) + 1, Int64.Type),
    #"Added DayName" = Table.AddColumn(#"Added DayOfWeek", "DayName", each Date.ToText([Date], "dddd"), type text),
    #"Added IsWeekend" = Table.AddColumn(#"Added DayName", "IsWeekend",
        each [DayOfWeekNumber] = 6 or [DayOfWeekNumber] = 7, type logical),
    #"Added IsCurrentMonth" = Table.AddColumn(#"Added IsWeekend", "IsCurrentMonth",
        each Date.IsInCurrentMonth([Date]), type logical),

    #"Reordered Columns" = Table.ReorderColumns(#"Added IsCurrentMonth",
        {"DateKey", "Date", "Year", "Quarter", "QuarterSortIndex", "FiscalQuarter", "FiscalYear",
         "Month", "MonthName", "MonthShortName", "MonthSortIndex", "WeekNumber",
         "DayOfWeekNumber", "DayName", "IsWeekend", "IsCurrentMonth"}),

    #"Set DateKey as Sorted Text-Safe Key" = Table.TransformColumnTypes(#"Reordered Columns", {{"DateKey", Int64.Type}})
in
    #"Set DateKey as Sorted Text-Safe Key"


// ----------------------------------------------------------------------------
// QUERY 2: Fact_Flights  (ingest + clean flight operations CSV)
// Create as a query named "Fact_Flights" pointing at Fact_Flights.csv
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("C:\FlightAnalytics\data\Fact_Flights.csv"),
        [Delimiter=",", Columns=25, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),

    // ---- Correct data types on ingest ----
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"FlightKey", Int64.Type}, {"FlightID", type text}, {"DateKey", Int64.Type},
        {"RouteKey", Int64.Type}, {"AircraftKey", Int64.Type}, {"DelayCodeKey", Int64.Type},
        {"ScheduledDepartureDateTime", type text}, {"ActualDepartureDateTime", type text},
        {"ScheduledArrivalDateTime", type text}, {"ActualArrivalDateTime", type text},
        {"ScheduledBlockMinutes", Int64.Type}, {"ActualBlockMinutes", Int64.Type},
        {"DepartureDelayMinutes", Int64.Type}, {"ArrivalDelayMinutes", Int64.Type},
        {"ReactionaryDelayMinutes", Int64.Type}, {"ScheduledTurnaroundMinutes", Int64.Type},
        {"ActualTurnaroundMinutes", Int64.Type}, {"SeatsAvailable", Int64.Type},
        {"PassengersBoarded", Int64.Type}, {"CargoKG", Int64.Type},
        {"FuelBurnPlannedKG", type number}, {"FuelBurnActualKG", type number},
        {"FlightStatus", type text}, {"IsCancelled", type logical}
    }),

    // ---- Robust datetime parsing (handles blank strings on cancelled flights) ----
    #"Parsed Scheduled Departure" = Table.TransformColumns(#"Changed Type",
        {{"ScheduledDepartureDateTime", each try DateTime.FromText(_) otherwise null, type nullable datetime}}),
    #"Parsed Actual Departure" = Table.TransformColumns(#"Parsed Scheduled Departure",
        {{"ActualDepartureDateTime", each try DateTime.FromText(_) otherwise null, type nullable datetime}}),
    #"Parsed Scheduled Arrival" = Table.TransformColumns(#"Parsed Actual Departure",
        {{"ScheduledArrivalDateTime", each try DateTime.FromText(_) otherwise null, type nullable datetime}}),
    #"Parsed Actual Arrival" = Table.TransformColumns(#"Parsed Scheduled Arrival",
        {{"ActualArrivalDateTime", each try DateTime.FromText(_) otherwise null, type nullable datetime}}),

    // ---- Calculate Flight Block Hours (actual, decimal hours, blank-safe) ----
    #"Added ActualBlockHours" = Table.AddColumn(#"Parsed Actual Arrival", "ActualBlockHours",
        each if [IsCancelled] = true or [ActualDepartureDateTime] = null or [ActualArrivalDateTime] = null
             then 0
             else Duration.TotalHours([ActualArrivalDateTime] - [ActualDepartureDateTime]),
        type number),
    #"Added ScheduledBlockHours" = Table.AddColumn(#"Added ActualBlockHours", "ScheduledBlockHours",
        each [ScheduledBlockMinutes] / 60, type number),

    // ---- Handle null / blank delay categories: force explicit "No Delay" key ----
    // (DelayCodeKey should never be null given the generator, but this guards
    //  against any future manual data entry gaps in the operational feed.)
    #"Filled Null Delay Codes" = Table.ReplaceValue(#"Added ScheduledBlockHours", null, 1,
        Replacer.ReplaceValue, {"DelayCodeKey"}),

    // ---- Derived OTP flag at the row grain (<=15 min departure buffer, excludes cancellations) ----
    #"Added IsOnTime15" = Table.AddColumn(#"Filled Null Delay Codes", "IsOnTime15Min",
        each if [IsCancelled] = true then null
             else [DepartureDelayMinutes] <= 15,
        type nullable logical),

    // ---- Data quality guard: drop any impossible negative block-time rows ----
    #"Removed Invalid Rows" = Table.SelectRows(#"Added IsOnTime15",
        each [ActualBlockHours] >= 0 and [ScheduledBlockMinutes] > 0),

    #"Reordered Columns" = Table.ReorderColumns(#"Removed Invalid Rows",
        {"FlightKey", "FlightID", "DateKey", "RouteKey", "AircraftKey", "DelayCodeKey",
         "ScheduledDepartureDateTime", "ActualDepartureDateTime", "ScheduledArrivalDateTime", "ActualArrivalDateTime",
         "ScheduledBlockMinutes", "ScheduledBlockHours", "ActualBlockMinutes", "ActualBlockHours",
         "DepartureDelayMinutes", "ArrivalDelayMinutes", "ReactionaryDelayMinutes", "IsOnTime15Min",
         "ScheduledTurnaroundMinutes", "ActualTurnaroundMinutes",
         "SeatsAvailable", "PassengersBoarded", "CargoKG",
         "FuelBurnPlannedKG", "FuelBurnActualKG", "FlightStatus", "IsCancelled"})
in
    #"Reordered Columns"


// ----------------------------------------------------------------------------
// QUERY 3: Fact_RouteFinancials  (ingest + type + derived unit economics staging)
// Create as a query named "Fact_RouteFinancials" pointing at Fact_RouteFinancials.csv
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("C:\FlightAnalytics\data\Fact_RouteFinancials.csv"),
        [Delimiter=",", Columns=17, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"RouteFinKey", Int64.Type}, {"DateKey", Int64.Type}, {"RouteKey", Int64.Type},
        {"AircraftKey", Int64.Type}, {"FlightCount", Int64.Type},
        {"ASK", Int64.Type}, {"RPK", Int64.Type},
        {"PassengerRevenueUSD", type number}, {"AncillaryRevenueUSD", type number},
        {"CargoRevenueUSD", type number}, {"TotalRevenueUSD", type number},
        {"FuelCostUSD", type number}, {"CrewCostUSD", type number},
        {"MaintenanceCostUSD", type number}, {"AirportChargesUSD", type number},
        {"OtherOperatingCostUSD", type number}, {"TotalOperatingCostUSD", type number}
    }),
    #"Removed Zero-ASK Rows" = Table.SelectRows(#"Changed Type", each [ASK] <> null and [ASK] > 0)
in
    #"Removed Zero-ASK Rows"

// ----------------------------------------------------------------------------
// Dim_Route / Dim_Aircraft / Dim_DelayCodes follow the same ingest pattern:
// Csv.Document -> Table.PromoteHeaders -> Table.TransformColumnTypes.
// They require no cleansing beyond correct type assignment since they are
// generated as clean reference tables.
// ----------------------------------------------------------------------------
