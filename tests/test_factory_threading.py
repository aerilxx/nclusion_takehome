import pytest
import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from factory import GameFactory, PlayerFactory
from models import Status


class TestGameFactoryThreadSafety:
    """Test thread safety of GameFactory"""
    
    @pytest.mark.asyncio
    async def test_concurrent_game_creation(self):
        """Test that concurrent game creation doesn't cause race conditions"""
        factory = GameFactory()
        
        async def create_game_task(name_suffix: int):
            return await factory.create_game(f"Game-{name_suffix}")
        
        # Create multiple games concurrently
        tasks = [create_game_task(i) for i in range(10)]
        games = await asyncio.gather(*tasks)
        
        # Verify all games have unique IDs
        game_ids = [game.id for game in games]
        assert len(set(game_ids)) == 10, "All games should have unique IDs"
        assert len(factory._games) == 10, "All games should be stored"
        
        # Verify sequential ID assignment
        assert sorted(game_ids) == list(range(1, 11)), "IDs should be sequential"
    
    @pytest.mark.asyncio
    async def test_concurrent_game_access(self):
        """Test that concurrent game access is thread-safe"""
        factory = GameFactory()
        
        # Create some games first
        for i in range(5):
            await factory.create_game(f"Game-{i}")
        
        async def get_game_task(game_id: int):
            return await factory.get_game(game_id)
        
        # Access games concurrently
        tasks = [get_game_task(i) for i in range(1, 6)]
        results = await asyncio.gather(*tasks)
        
        # Verify all games were retrieved correctly
        assert all(game is not None for game in results)
        assert [game.id for game in results] == list(range(1, 6))
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_mixed(self):
        """Test mixed concurrent operations (create, get, remove, get_all)"""
        factory = GameFactory()
        
        async def create_games():
            for i in range(5):
                await factory.create_game(f"CreateTest-{i}")
        
        async def get_games():
            results = []
            for i in range(1, 6):
                game = await factory.get_game(i)
                results.append(game)
            return results
        
        async def get_all_games():
            return await factory.get_all_games()
        
        async def get_count():
            return await factory.get_game_count()
        
        # Run all operations concurrently
        create_task = asyncio.create_task(create_games())
        get_task = asyncio.create_task(get_games())
        get_all_task = asyncio.create_task(get_all_games())
        count_task = asyncio.create_task(get_count())
        
        await asyncio.gather(create_task, get_task, get_all_task, count_task)
        
        # Verify final state
        final_count = await factory.get_game_count()
        all_games = await factory.get_all_games()
        assert final_count == 5
        assert len(all_games) == 5


class TestPlayerFactoryThreadSafety:
    """Test thread safety of PlayerFactory"""
    
    @pytest.mark.asyncio
    async def test_concurrent_player_creation(self):
        """Test that concurrent player creation doesn't cause race conditions"""
        factory = PlayerFactory()
        
        async def create_player_task(player_id: str):
            return await factory.get_or_create_player(
                player_id=f"player-{player_id}",
                email=f"player{player_id}@example.com",
                name=f"Player {player_id}"
            )
        
        # Create multiple players concurrently
        tasks = [create_player_task(str(i)) for i in range(10)]
        players = await asyncio.gather(*tasks)
        
        # Verify all players have unique IDs
        player_ids = [player.id for player in players]
        assert len(set(player_ids)) == 10, "All players should have unique IDs"
        assert len(factory._players) == 10, "All players should be stored"
    
    @pytest.mark.asyncio
    async def test_concurrent_duplicate_player_creation(self):
        """Test that creating the same player concurrently returns the same instance"""
        factory = PlayerFactory()
        
        async def create_same_player():
            return await factory.get_or_create_player(
                player_id="duplicate-player",
                email="duplicate@example.com",
                name="Duplicate Player"
            )
        
        # Try to create the same player multiple times concurrently
        tasks = [create_same_player() for _ in range(5)]
        players = await asyncio.gather(*tasks)
        
        # All should be the same instance
        first_player = players[0]
        assert all(player is first_player for player in players), "Should return same instance"
        assert len(factory._players) == 1, "Only one player should be stored"
    
    @pytest.mark.asyncio
    async def test_race_condition_get_player(self):
        """Test potential race condition in get_player method"""
        factory = PlayerFactory()
        
        # Add a player
        await factory.get_or_create_player("test-player", "test@example.com", "Test Player")
        
        async def get_player_while_modifying():
            """Try to get a player while dictionary might be modified"""
            return await factory.get_player("test-player")
        
        async def modify_players():
            """Continuously modify the players dictionary"""
            for i in range(10):
                await factory.get_or_create_player(f"temp-{i}", f"temp{i}@example.com", f"Temp {i}")
                await asyncio.sleep(0.001)  # Small delay to increase chance of race condition
        
        # Run get operations concurrent with modifications
        get_tasks = [get_player_while_modifying() for _ in range(20)]
        modify_task = asyncio.create_task(modify_players())
        
        # This might fail if there's a race condition
        results = await asyncio.gather(*get_tasks, return_exceptions=True)
        await modify_task
        
        # Check if any operations failed due to race conditions
        exceptions = [r for r in results if isinstance(r, Exception)]
        if exceptions:
            pytest.fail(f"Race condition detected: {exceptions[0]}")
        
        # All successful results should be the same player or None
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert all(r.id == "test-player" for r in successful_results if r is not None)
    
    @pytest.mark.asyncio
    async def test_race_condition_all_players(self):
        """Test potential race condition in all_players method"""
        factory = PlayerFactory()
        
        # Add some initial players
        for i in range(5):
            await factory.get_or_create_player(f"initial-{i}", f"initial{i}@example.com", f"Initial {i}")
        
        async def get_all_players():
            """Try to get all players while dictionary might be modified"""
            return await factory.all_players()
        
        async def modify_players():
            """Continuously modify the players dictionary"""
            for i in range(10):
                await factory.get_or_create_player(f"dynamic-{i}", f"dynamic{i}@example.com", f"Dynamic {i}")
                await asyncio.sleep(0.001)  # Small delay to increase chance of race condition
        
        # Run get_all operations concurrent with modifications
        get_all_tasks = [get_all_players() for _ in range(10)]
        modify_task = asyncio.create_task(modify_players())
        
        # This might fail if there's a race condition
        results = await asyncio.gather(*get_all_tasks, return_exceptions=True)
        await modify_task
        
        # Check if any operations failed due to race conditions
        exceptions = [r for r in results if isinstance(r, Exception)]
        if exceptions:
            pytest.fail(f"Race condition detected: {exceptions[0]}")
        
        # All successful results should be lists
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert all(isinstance(r, list) for r in successful_results)
    
    @pytest.mark.asyncio 
    async def test_lock_effectiveness(self):
        """Test that the locks actually prevent race conditions"""
        factory = PlayerFactory()
        
        # Use a counter to track lock acquisitions
        lock_acquisitions = []
        original_acquire = factory._lock.acquire
        
        async def tracking_acquire():
            result = await original_acquire()
            lock_acquisitions.append(asyncio.current_task())
            return result
        
        # Mock the lock to track acquisitions
        with patch.object(factory._lock, 'acquire', side_effect=tracking_acquire):
            # Create players concurrently
            tasks = []
            for i in range(5):
                task = asyncio.create_task(
                    factory.get_or_create_player(f"player-{i}", f"player{i}@example.com", f"Player {i}")
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks)
        
        # Verify that locks were acquired (indicating proper synchronization)
        assert len(lock_acquisitions) == 5, "Each operation should acquire the lock"
    
    @pytest.mark.asyncio
    async def test_thread_safe_get_player_fixed(self):
        """Test that the fixed get_player method is now thread-safe"""
        factory = PlayerFactory()
        
        # Add a player
        await factory.get_or_create_player("test-player", "test@example.com", "Test Player")
        
        async def get_player_concurrent():
            return await factory.get_player("test-player")
        
        async def modify_players_concurrent():
            for i in range(10):
                await factory.get_or_create_player(f"concurrent-{i}", f"concurrent{i}@example.com", f"Concurrent {i}")
        
        # Run many get operations concurrent with modifications
        get_tasks = [get_player_concurrent() for _ in range(50)]
        modify_task = asyncio.create_task(modify_players_concurrent())
        
        results = await asyncio.gather(*get_tasks)
        await modify_task
        
        # All results should be the same player (the one we're looking for)
        assert all(player is not None and player.id == "test-player" for player in results)
        
        # Verify all concurrent players were created
        final_count = await factory.get_player_count()
        assert final_count == 11  # 1 original + 10 concurrent
    
    @pytest.mark.asyncio
    async def test_thread_safe_all_players_fixed(self):
        """Test that the fixed all_players method is now thread-safe"""
        factory = PlayerFactory()
        
        # Add some initial players
        for i in range(5):
            await factory.get_or_create_player(f"initial-{i}", f"initial{i}@example.com", f"Initial {i}")
        
        async def get_all_concurrent():
            return await factory.all_players()
        
        async def modify_players_concurrent():
            for i in range(10):
                await factory.get_or_create_player(f"added-{i}", f"added{i}@example.com", f"Added {i}")
        
        # Run many all_players operations concurrent with modifications
        get_all_tasks = [get_all_concurrent() for _ in range(20)]
        modify_task = asyncio.create_task(modify_players_concurrent())
        
        results = await asyncio.gather(*get_all_tasks)
        await modify_task
        
        # All results should be valid lists
        assert all(isinstance(result, list) for result in results)
        
        # Verify final state
        final_players = await factory.all_players()
        final_count = await factory.get_player_count()
        assert len(final_players) == final_count == 15  # 5 initial + 10 added
    
    @pytest.mark.asyncio
    async def test_comprehensive_thread_safety(self):
        """Comprehensive test of all PlayerFactory operations under high concurrency"""
        factory = PlayerFactory()
        
        async def worker(worker_id: int):
            """Each worker performs various operations"""
            results = {}
            
            # Create players
            player = await factory.get_or_create_player(
                f"worker-{worker_id}", 
                f"worker{worker_id}@example.com", 
                f"Worker {worker_id}"
            )
            results['created'] = player
            
            # Get the same player
            retrieved = await factory.get_player(f"worker-{worker_id}")
            results['retrieved'] = retrieved
            
            # Get all players
            all_players = await factory.all_players()
            results['all_count'] = len(all_players)
            
            # Get count
            count = await factory.get_player_count()
            results['count'] = count
            
            return results
        
        # Run 20 workers concurrently
        worker_tasks = [worker(i) for i in range(20)]
        all_results = await asyncio.gather(*worker_tasks)
        
        # Verify results
        for i, result in enumerate(all_results):
            assert result['created'].id == f"worker-{i}"
            assert result['retrieved'].id == f"worker-{i}"
            assert result['created'] is result['retrieved']  # Should be same instance
        
        # Verify final state
        final_count = await factory.get_player_count()
        final_players = await factory.all_players()
        assert final_count == 20
        assert len(final_players) == 20
        
        # Verify all workers are present
        worker_ids = {player.id for player in final_players}
        expected_ids = {f"worker-{i}" for i in range(20)}
        assert worker_ids == expected_ids


if __name__ == "__main__":
    pytest.main([__file__])
