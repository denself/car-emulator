from utils.clock import IClock, Clock, HistoricalClock

manager ={
    IClock: {
        'default': Clock,
        'historical': HistoricalClock
    }
}

# def J(interface):
#     cls =