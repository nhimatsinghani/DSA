"""
Real-world Examples of Skip List Usage
=====================================

Practical examples demonstrating how Skip Lists can be used
in various real-world scenarios.
"""

from skiplist import SkipList, create_skip_list_from_list
import random
import time
from datetime import datetime, timedelta
from typing import List, Tuple


class LeaderboardSystem:
    """
    Gaming leaderboard system using Skip List.
    
    Maintains player scores in sorted order for efficient
    rank queries and score updates.
    """
    
    def __init__(self):
        self.leaderboard = SkipList()
        self.players = {}  # player_id -> (score, name)
    
    def add_player(self, player_id: str, name: str, score: int):
        """Add a new player to the leaderboard."""
        # Use negative score for descending order (highest scores first)
        key = (-score, player_id)  # Secondary sort by player_id for ties
        self.leaderboard.insert(key, {"name": name, "score": score, "player_id": player_id})
        self.players[player_id] = (score, name)
        print(f"Added {name} with score {score}")
    
    def update_score(self, player_id: str, new_score: int):
        """Update a player's score."""
        if player_id not in self.players:
            print(f"Player {player_id} not found")
            return
        
        old_score, name = self.players[player_id]
        
        # Remove old entry
        old_key = (-old_score, player_id)
        self.leaderboard.delete(old_key)
        
        # Add new entry
        new_key = (-new_score, player_id)
        self.leaderboard.insert(new_key, {"name": name, "score": new_score, "player_id": player_id})
        self.players[player_id] = (new_score, name)
        
        print(f"Updated {name}: {old_score} → {new_score}")
    
    def get_top_n(self, n: int) -> List[dict]:
        """Get top N players."""
        result = []
        count = 0
        for key, player_data in self.leaderboard:
            if count >= n:
                break
            result.append(player_data)
            count += 1
        return result
    
    def get_rank(self, player_id: str) -> int:
        """Get a player's rank (1-indexed)."""
        if player_id not in self.players:
            return -1
        
        score, _ = self.players[player_id]
        target_key = (-score, player_id)
        
        rank = 1
        for key, _ in self.leaderboard:
            if key == target_key:
                return rank
            rank += 1
        return -1
    
    def get_score_range(self, min_score: int, max_score: int) -> List[dict]:
        """Get players within a score range."""
        # Convert to negative scores and swap order for range query
        start_key = (-max_score, "")  # Start with highest score
        end_key = (-min_score, "zzz")  # End with lowest score
        
        results = self.leaderboard.range_query(start_key, end_key)
        return [player_data for _, player_data in results]


class EventScheduler:
    """
    Event scheduling system using Skip List.
    
    Maintains events in chronological order for efficient
    time-based queries and scheduling operations.
    """
    
    def __init__(self):
        self.schedule = SkipList()
        self.event_counter = 0
    
    def schedule_event(self, timestamp: datetime, title: str, description: str = ""):
        """Schedule a new event."""
        self.event_counter += 1
        event_id = self.event_counter
        
        # Use timestamp as key, event_id as tiebreaker
        key = (timestamp.timestamp(), event_id)
        event_data = {
            "id": event_id,
            "timestamp": timestamp,
            "title": title,
            "description": description
        }
        
        self.schedule.insert(key, event_data)
        print(f"Scheduled: {title} at {timestamp.strftime('%Y-%m-%d %H:%M')}")
        return event_id
    
    def cancel_event(self, event_id: int) -> bool:
        """Cancel an event by ID."""
        # Need to find the event first
        for key, event_data in self.schedule:
            if event_data["id"] == event_id:
                self.schedule.delete(key)
                print(f"Cancelled: {event_data['title']}")
                return True
        print(f"Event {event_id} not found")
        return False
    
    def get_events_in_range(self, start_time: datetime, end_time: datetime) -> List[dict]:
        """Get all events in a time range."""
        start_key = (start_time.timestamp(), 0)
        end_key = (end_time.timestamp(), float('inf'))
        
        results = self.schedule.range_query(start_key, end_key)
        return [event_data for _, event_data in results]
    
    def get_next_events(self, n: int) -> List[dict]:
        """Get next N upcoming events."""
        now = datetime.now()
        result = []
        count = 0
        
        for key, event_data in self.schedule:
            if event_data["timestamp"] >= now and count < n:
                result.append(event_data)
                count += 1
            elif count >= n:
                break
        
        return result
    
    def get_todays_events(self) -> List[dict]:
        """Get all events for today."""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        return self.get_events_in_range(today, tomorrow)


class OrderBook:
    """
    Stock trading order book using Skip Lists.
    
    Maintains buy and sell orders sorted by price for efficient
    order matching and market data queries.
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        # Buy orders: highest price first (negative prices)
        self.buy_orders = SkipList()
        # Sell orders: lowest price first (positive prices)
        self.sell_orders = SkipList()
        self.order_counter = 0
    
    def add_buy_order(self, price: float, quantity: int, trader_id: str) -> int:
        """Add a buy order."""
        self.order_counter += 1
        order_id = self.order_counter
        
        # Use negative price for descending order (highest price first)
        key = (-price, order_id)
        order_data = {
            "id": order_id,
            "price": price,
            "quantity": quantity,
            "trader_id": trader_id,
            "type": "buy",
            "timestamp": datetime.now()
        }
        
        self.buy_orders.insert(key, order_data)
        print(f"Buy order {order_id}: {quantity} @ ${price:.2f}")
        return order_id
    
    def add_sell_order(self, price: float, quantity: int, trader_id: str) -> int:
        """Add a sell order."""
        self.order_counter += 1
        order_id = self.order_counter
        
        # Use positive price for ascending order (lowest price first)
        key = (price, order_id)
        order_data = {
            "id": order_id,
            "price": price,
            "quantity": quantity,
            "trader_id": trader_id,
            "type": "sell",
            "timestamp": datetime.now()
        }
        
        self.sell_orders.insert(key, order_data)
        print(f"Sell order {order_id}: {quantity} @ ${price:.2f}")
        return order_id
    
    def get_best_bid(self) -> dict:
        """Get the highest buy order (best bid)."""
        if len(self.buy_orders) == 0:
            return None
        
        for _, order_data in self.buy_orders:
            return order_data
    
    def get_best_ask(self) -> dict:
        """Get the lowest sell order (best ask)."""
        if len(self.sell_orders) == 0:
            return None
        
        for _, order_data in self.sell_orders:
            return order_data
    
    def get_spread(self) -> float:
        """Get the bid-ask spread."""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        
        if best_bid and best_ask:
            return best_ask["price"] - best_bid["price"]
        return None
    
    def get_depth(self, levels: int = 5) -> dict:
        """Get market depth (top N levels of buy/sell orders)."""
        buy_depth = []
        sell_depth = []
        
        # Get top buy orders
        count = 0
        for _, order_data in self.buy_orders:
            if count >= levels:
                break
            buy_depth.append(order_data)
            count += 1
        
        # Get top sell orders
        count = 0
        for _, order_data in self.sell_orders:
            if count >= levels:
                break
            sell_depth.append(order_data)
            count += 1
        
        return {"buys": buy_depth, "sells": sell_depth}


class CacheSystem:
    """
    LRU Cache system using Skip List for time-based ordering.
    
    Maintains cache entries sorted by access time for efficient
    LRU eviction and time-based queries.
    """
    
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.cache_data = {}  # key -> value
        self.access_times = SkipList()  # (timestamp, key) -> access_info
        self.access_counter = 0
    
    def get(self, key: str):
        """Get value from cache."""
        if key not in self.cache_data:
            return None
        
        # Update access time
        self._update_access_time(key)
        return self.cache_data[key]
    
    def put(self, key: str, value):
        """Put value in cache."""
        if key in self.cache_data:
            # Update existing key
            self.cache_data[key] = value
            self._update_access_time(key)
        else:
            # Add new key
            if len(self.cache_data) >= self.max_size:
                self._evict_lru()
            
            self.cache_data[key] = value
            self._update_access_time(key)
    
    def _update_access_time(self, key: str):
        """Update access time for a key."""
        # Remove old access time entry if exists
        for access_key, access_info in list(self.access_times):
            if access_info["key"] == key:
                self.access_times.delete(access_key)
                break
        
        # Add new access time entry
        self.access_counter += 1
        access_key = (time.time(), self.access_counter)
        access_info = {"key": key, "timestamp": time.time()}
        self.access_times.insert(access_key, access_info)
    
    def _evict_lru(self):
        """Evict least recently used item."""
        if len(self.access_times) == 0:
            return
        
        # Get the first (oldest) access time entry
        for access_key, access_info in self.access_times:
            lru_key = access_info["key"]
            
            # Remove from both data structures
            del self.cache_data[lru_key]
            self.access_times.delete(access_key)
            print(f"Evicted LRU key: {lru_key}")
            break
    
    def get_statistics(self) -> dict:
        """Get cache statistics."""
        return {
            "size": len(self.cache_data),
            "max_size": self.max_size,
            "keys": list(self.cache_data.keys()),
            "access_order": [info["key"] for _, info in self.access_times]
        }


def demo_leaderboard():
    """Demonstrate leaderboard system."""
    print("=" * 60)
    print("LEADERBOARD SYSTEM DEMO")
    print("=" * 60)
    
    leaderboard = LeaderboardSystem()
    
    # Add players
    players = [
        ("player1", "Alice", 2500),
        ("player2", "Bob", 1800),
        ("player3", "Charlie", 3200),
        ("player4", "Diana", 2100),
        ("player5", "Eve", 2900),
    ]
    
    for player_id, name, score in players:
        leaderboard.add_player(player_id, name, score)
    
    print(f"\nTop 3 players:")
    for i, player in enumerate(leaderboard.get_top_n(3), 1):
        print(f"  {i}. {player['name']}: {player['score']}")
    
    print(f"\nCharlie's rank: {leaderboard.get_rank('player3')}")
    
    # Update score
    leaderboard.update_score("player2", 3500)
    
    print(f"\nTop 3 after Bob's score update:")
    for i, player in enumerate(leaderboard.get_top_n(3), 1):
        print(f"  {i}. {player['name']}: {player['score']}")
    
    # Score range query
    high_scorers = leaderboard.get_score_range(2500, 4000)
    print(f"\nPlayers with scores 2500-4000:")
    for player in high_scorers:
        print(f"  {player['name']}: {player['score']}")


def demo_event_scheduler():
    """Demonstrate event scheduling system."""
    print("\n" + "=" * 60)
    print("EVENT SCHEDULER DEMO")
    print("=" * 60)
    
    scheduler = EventScheduler()
    
    # Schedule events
    now = datetime.now()
    events = [
        (now + timedelta(hours=1), "Team Meeting", "Weekly sync"),
        (now + timedelta(hours=3), "Code Review", "PR #123"),
        (now + timedelta(days=1), "Sprint Planning", "Next iteration"),
        (now + timedelta(hours=0.5), "Coffee Break", "Informal chat"),
        (now + timedelta(days=2), "Demo Day", "Show and tell"),
    ]
    
    event_ids = []
    for timestamp, title, description in events:
        event_id = scheduler.schedule_event(timestamp, title, description)
        event_ids.append(event_id)
    
    print(f"\nNext 3 upcoming events:")
    for event in scheduler.get_next_events(3):
        time_str = event["timestamp"].strftime("%Y-%m-%d %H:%M")
        print(f"  {time_str}: {event['title']}")
    
    # Cancel an event
    scheduler.cancel_event(event_ids[1])
    
    print(f"\nEvents in next 2 hours:")
    end_time = now + timedelta(hours=2)
    for event in scheduler.get_events_in_range(now, end_time):
        time_str = event["timestamp"].strftime("%H:%M")
        print(f"  {time_str}: {event['title']}")


def demo_order_book():
    """Demonstrate order book system."""
    print("\n" + "=" * 60)
    print("ORDER BOOK DEMO")
    print("=" * 60)
    
    book = OrderBook("AAPL")
    
    # Add buy orders
    buy_orders = [
        (150.25, 100, "trader1"),
        (150.20, 200, "trader2"),
        (150.30, 150, "trader3"),
        (150.15, 300, "trader4"),
    ]
    
    for price, quantity, trader in buy_orders:
        book.add_buy_order(price, quantity, trader)
    
    print()
    
    # Add sell orders
    sell_orders = [
        (150.35, 100, "trader5"),
        (150.40, 200, "trader6"),
        (150.32, 150, "trader7"),
        (150.45, 300, "trader8"),
    ]
    
    for price, quantity, trader in sell_orders:
        book.add_sell_order(price, quantity, trader)
    
    # Show market data
    best_bid = book.get_best_bid()
    best_ask = book.get_best_ask()
    spread = book.get_spread()
    
    print(f"\nMarket Data:")
    print(f"  Best Bid: ${best_bid['price']:.2f} x {best_bid['quantity']}")
    print(f"  Best Ask: ${best_ask['price']:.2f} x {best_ask['quantity']}")
    print(f"  Spread: ${spread:.2f}")
    
    print(f"\nMarket Depth:")
    depth = book.get_depth(3)
    print("  Buys:")
    for order in depth["buys"]:
        print(f"    ${order['price']:.2f} x {order['quantity']}")
    print("  Sells:")
    for order in depth["sells"]:
        print(f"    ${order['price']:.2f} x {order['quantity']}")


def demo_cache_system():
    """Demonstrate cache system."""
    print("\n" + "=" * 60)
    print("CACHE SYSTEM DEMO")
    print("=" * 60)
    
    cache = CacheSystem(max_size=3)
    
    # Add items to cache
    cache.put("key1", "value1")
    cache.put("key2", "value2")
    cache.put("key3", "value3")
    
    print("Added 3 items to cache")
    print(f"Cache stats: {cache.get_statistics()}")
    
    # Access some items
    print(f"\nAccessing key1: {cache.get('key1')}")
    print(f"Accessing key3: {cache.get('key3')}")
    
    # Add another item (should evict LRU)
    cache.put("key4", "value4")
    print(f"\nAfter adding key4:")
    print(f"Cache stats: {cache.get_statistics()}")
    
    # Try to access evicted item
    print(f"\nTrying to access key2: {cache.get('key2')}")


def main():
    """Run all example demonstrations."""
    print("Skip List Real-world Examples")
    print("=" * 60)
    
    examples = [
        demo_leaderboard,
        demo_event_scheduler,
        demo_order_book,
        demo_cache_system,
    ]
    
    for demo_func in examples:
        try:
            demo_func()
        except KeyboardInterrupt:
            print("\nDemo interrupted by user")
            break
        except Exception as e:
            print(f"\nError in demo: {e}")
    
    print("\nAll demos completed!")


if __name__ == "__main__":
    main() 