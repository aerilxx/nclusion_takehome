# This unit test is to test multi-threading safe of GameFactory and PlayerFactory,
# however cannot incorporate into pytest due to complexity of setting up relative path without
# modulize the src.

# import pytest
# import asyncio

# import sys
# import os
# sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# from factory import GameFactory, PlayerFactory


# class TestGameFactoryThreadSafety:
#     """Test thread safety of GameFactory"""
    
#     @pytest.mark.asyncio
#     async def test_concurrent_game_creation(self):
#         """Test that concurrent game creation doesn't cause race conditions"""
#         factory = GameFactory()
        
#         async def create_game_task(name_suffix: int):
#             return await factory.create_game(f"Game-{name_suffix}")
        
#         # Create multiple games concurrently
#         tasks = [create_game_task(i) for i in range(10)]
#         games = await asyncio.gather(*tasks)
        
#         # Verify all games have unique IDs
#         game_ids = [game.id for game in games]
#         assert len(set(game_ids)) == 10, "All games should have unique IDs"
#         assert len(factory._games) == 10, "All games should be stored"
        
#         # Verify sequential ID assignment
#         assert sorted(game_ids) == list(range(1, 11)), "IDs should be sequential"
    
#     @pytest.mark.asyncio
#     async def test_concurrent_game_access(self):
#         """Test that concurrent game access is thread-safe"""
#         factory = GameFactory()
        
#         # Create some games first
#         for i in range(5):
#             await factory.create_game(f"Game-{i}")
        
#         async def get_game_task(game_id: int):
#             return await factory.get_game(game_id)
        
#         # Access games concurrently
#         tasks = [get_game_task(i) for i in range(1, 6)]
#         results = await asyncio.gather(*tasks)
        
#         # Verify all games were retrieved correctly
#         assert all(game is not None for game in results)
#         assert [game.id for game in results] == list(range(1, 6))
    
#     @pytest.mark.asyncio
#     async def test_concurrent_operations_mixed(self):
#         """Test mixed concurrent operations (create, get, remove, get_all)"""
#         factory = GameFactory()
        
#         async def create_games():
#             for i in range(5):
#                 await factory.create_game(f"CreateTest-{i}")
        
#         async def get_games():
#             results = []
#             for i in range(1, 6):
#                 game = await factory.get_game(i)
#                 results.append(game)
#             return results
        
#         async def get_all_games():
#             return await factory.get_all_games()
        
#         async def get_count():
#             return await factory.get_game_count()
        
#         # Run all operations concurrently
#         create_task = asyncio.create_task(create_games())
#         get_task = asyncio.create_task(get_games())
#         get_all_task = asyncio.create_task(get_all_games())
#         count_task = asyncio.create_task(get_count())
        
#         await asyncio.gather(create_task, get_task, get_all_task, count_task)
        
#         # Verify final state
#         final_count = await factory.get_game_count()
#         all_games = await factory.get_all_games()
#         assert final_count == 5
#         assert len(all_games) == 5


# class TestPlayerFactoryThreadSafety:
#     """Test thread safety of PlayerFactory"""
    
#     @pytest.mark.asyncio
#     async def test_concurrent_player_creation(self):
#         """Test that concurrent player creation doesn't cause race conditions"""
#         factory = PlayerFactory()
        
#         async def create_player_task(player_id: str):
#             return await factory.get_or_create_player(
#                 player_id=f"player-{player_id}",
#                 email=f"player{player_id}@example.com",
#                 name=f"Player {player_id}"
#             )
        
#         # Create multiple players concurrently
#         tasks = [create_player_task(str(i)) for i in range(10)]
#         players = await asyncio.gather(*tasks)
        
#         # Verify all players have unique IDs
#         player_ids = [player.id for player in players]
#         assert len(set(player_ids)) == 10, "All players should have unique IDs"
#         assert len(factory._players) == 10, "All players should be stored"
    
#     @pytest.mark.asyncio
#     async def test_concurrent_duplicate_player_creation(self):
#         """Test that creating the same player concurrently returns the same instance"""
#         factory = PlayerFactory()
        
#         async def create_same_player():
#             return await factory.get_or_create_player(
#                 player_id="duplicate-player",
#                 email="duplicate@example.com",
#                 name="Duplicate Player"
#             )
        
#         # Try to create the same player multiple times concurrently
#         tasks = [create_same_player() for _ in range(5)]
#         players = await asyncio.gather(*tasks)
        
#         # All should be the same instance
#         first_player = players[0]
#         assert all(player is first_player for player in players), "Should return same instance"
#         assert len(factory._players) == 1, "Only one player should be stored"
    
#     @pytest.mark.asyncio
#     async def test_comprehensive_thread_safety(self):
#         """Comprehensive test of all PlayerFactory operations under high concurrency"""
#         factory = PlayerFactory()
        
#         async def worker(worker_id: int):
#             """Each worker performs various operations"""
#             results = {}
            
#             # Create players
#             player = await factory.get_or_create_player(
#                 f"worker-{worker_id}", 
#                 f"worker{worker_id}@example.com", 
#                 f"Worker {worker_id}"
#             )
#             results['created'] = player
            
#             # Get the same player
#             retrieved = await factory.get_player(f"worker-{worker_id}")
#             results['retrieved'] = retrieved
            
#             # Get all players
#             all_players = await factory.all_players()
#             results['all_count'] = len(all_players)
            
#             # Get count
#             count = await factory.get_player_count()
#             results['count'] = count
#             return results
        
#         # Run 20 workers concurrently
#         worker_tasks = [worker(i) for i in range(20)]
#         all_results = await asyncio.gather(*worker_tasks)
        
#         # Verify results
#         for i, result in enumerate(all_results):
#             assert result['created'].id == f"worker-{i}"
#             assert result['retrieved'].id == f"worker-{i}"
#             assert result['created'] is result['retrieved']  # Should be same instance
        
#         # Verify final state
#         final_count = await factory.get_player_count()
#         final_players = await factory.all_players()
#         assert final_count == 20
#         assert len(final_players) == 20
        
#         # Verify all workers are present
#         worker_ids = {player.id for player in final_players}
#         expected_ids = {f"worker-{i}" for i in range(20)}
#         assert worker_ids == expected_ids


# if __name__ == "__main__":
#     pytest.main([__file__])
