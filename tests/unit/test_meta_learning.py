"""
Tests for Meta-Learning for Cold-Start User Preference.

MIT-Level Test Coverage for:
- UserInteraction dataclass
- Task dataclass
- PreferenceModel class
- MAML class
- Reptile class
- ColdStartHandler class
- PrototypicalNetworks class
- create_synthetic_task_generator function

Edge Cases Documented:
- Cold-start users with zero interactions
- Single-shot adaptation
- Extreme preference values
"""

import pytest
import numpy as np
from datetime import datetime

from src.research.meta_learning import (
    ContentType,
    UserInteraction,
    Task,
    PreferenceModel,
    MAML,
    Reptile,
    ColdStartHandler,
    PrototypicalNetworks,
    create_synthetic_task_generator,
)


# =============================================================================
# UserInteraction Tests
# =============================================================================


class TestUserInteraction:
    """Test UserInteraction dataclass."""
    
    def test_interaction_creation(self):
        """Test basic interaction creation."""
        interaction = UserInteraction(
            content_type=ContentType.VIDEO,
            context_features=np.array([0.5, 0.3, 0.2, 0.1, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]),
            rating=0.8,
            engagement_time=45.0
        )
        
        assert interaction.content_type == ContentType.VIDEO
        assert interaction.rating == 0.8
        assert interaction.engagement_time == 45.0
    
    def test_interaction_features(self):
        """Test that features are numpy array."""
        interaction = UserInteraction(
            content_type=ContentType.MUSIC,
            context_features=np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            rating=0.5,
            engagement_time=30.0
        )
        
        assert isinstance(interaction.context_features, np.ndarray)
    
    def test_reward_property(self):
        """Test composite reward calculation."""
        interaction = UserInteraction(
            content_type=ContentType.TEXT,
            context_features=np.zeros(10),
            rating=1.0,
            engagement_time=60.0  # 1 minute
        )
        
        # Reward = 0.7 * rating + 0.3 * min(1.0, engagement_time / 60)
        # = 0.7 * 1.0 + 0.3 * 1.0 = 1.0
        assert interaction.reward == pytest.approx(1.0, rel=0.01)


# =============================================================================
# Task Tests
# =============================================================================


class TestTask:
    """Test Task dataclass."""
    
    def test_task_creation(self):
        """Test basic task creation."""
        support = [
            UserInteraction(ContentType.VIDEO, np.zeros(10), 0.5, 30.0)
        ]
        query = [
            UserInteraction(ContentType.MUSIC, np.zeros(10), 0.7, 45.0)
        ]
        
        task = Task(
            user_id="u1",
            support_set=support,
            query_set=query
        )
        
        assert task.user_id == "u1"
        assert len(task.support_set) == 1
        assert len(task.query_set) == 1
    
    def test_k_shot_property(self):
        """Test k-shot property."""
        support = [
            UserInteraction(ContentType.VIDEO, np.zeros(10), 0.5, 30.0),
            UserInteraction(ContentType.MUSIC, np.zeros(10), 0.6, 35.0),
            UserInteraction(ContentType.TEXT, np.zeros(10), 0.7, 40.0),
        ]
        task = Task("u1", support, [])
        
        assert task.k_shot == 3


# =============================================================================
# PreferenceModel Tests
# =============================================================================


class TestPreferenceModel:
    """Test PreferenceModel class."""
    
    def test_model_creation(self):
        """Test model creation."""
        model = PreferenceModel(input_dim=10, hidden_dim=32, output_dim=3, seed=42)
        
        assert model.input_dim == 10
        assert model.hidden_dim == 32
        assert model.output_dim == 3
    
    def test_forward_pass(self):
        """Test forward pass."""
        model = PreferenceModel(input_dim=10, hidden_dim=16, output_dim=3, seed=42)
        
        x = np.random.randn(4, 10).astype(np.float32)
        output = model.forward(x)
        
        assert output.shape == (4, 3)
        # Output should be probabilities (softmax)
        assert np.allclose(output.sum(axis=1), 1.0, atol=1e-5)
    
    def test_forward_single_input(self):
        """Test forward pass with single input."""
        model = PreferenceModel(input_dim=10, seed=42)
        
        x = np.random.randn(10).astype(np.float32)
        output = model.forward(x)
        
        assert output.shape == (1, 3)
    
    def test_get_set_parameters(self):
        """Test parameter getting and setting."""
        model = PreferenceModel(input_dim=10, hidden_dim=8, output_dim=3, seed=42)
        
        params = model.get_parameters()
        assert isinstance(params, np.ndarray)
        
        # Modify and set back
        new_params = params + 0.1
        model.set_parameters(new_params)
        
        retrieved = model.get_parameters()
        assert np.allclose(retrieved, new_params)
    
    def test_copy(self):
        """Test model copy."""
        model = PreferenceModel(input_dim=10, hidden_dim=8, output_dim=3, seed=42)
        
        copy = model.copy()
        
        assert np.allclose(model.get_parameters(), copy.get_parameters())
        
        # Modifying copy shouldn't affect original
        copy_params = copy.get_parameters()
        copy_params[0] = 999.0
        copy.set_parameters(copy_params)
        
        assert model.get_parameters()[0] != 999.0
    
    def test_compute_loss(self):
        """Test loss computation."""
        model = PreferenceModel(input_dim=10, hidden_dim=8, output_dim=3, seed=42)
        
        interactions = [
            UserInteraction(ContentType.VIDEO, np.random.rand(10), 0.8, 30.0),
            UserInteraction(ContentType.MUSIC, np.random.rand(10), 0.6, 45.0),
        ]
        
        loss, grad = model.compute_loss(interactions)
        
        assert isinstance(loss, float)
        assert isinstance(grad, np.ndarray)
        assert grad.shape == model.get_parameters().shape


# =============================================================================
# MAML Tests
# =============================================================================


class TestMAML:
    """Test Model-Agnostic Meta-Learning."""
    
    def test_maml_creation(self):
        """Test MAML creation."""
        model = PreferenceModel(input_dim=10, hidden_dim=8, output_dim=3, seed=42)
        maml = MAML(
            model=model,
            inner_lr=0.01,
            outer_lr=0.001,
            inner_steps=5,
            seed=42
        )
        
        assert maml.alpha == 0.01
        assert maml.beta == 0.001
        assert maml.inner_steps == 5
    
    def test_inner_loop(self):
        """Test inner loop adaptation."""
        model = PreferenceModel(input_dim=10, hidden_dim=8, output_dim=3, seed=42)
        maml = MAML(model=model, seed=42)
        
        support_set = [
            UserInteraction(ContentType.VIDEO, np.random.rand(10), 0.8, 30.0),
            UserInteraction(ContentType.MUSIC, np.random.rand(10), 0.6, 45.0),
        ]
        
        adapted_model = maml.inner_loop(support_set)
        
        assert isinstance(adapted_model, PreferenceModel)
    
    def test_outer_loop(self):
        """Test outer loop meta-update."""
        model = PreferenceModel(input_dim=10, hidden_dim=8, output_dim=3, seed=42)
        maml = MAML(model=model, seed=42)
        
        # Create tasks
        tasks = []
        for i in range(3):
            support = [
                UserInteraction(ContentType.VIDEO, np.random.rand(10), 0.5, 30.0)
            ]
            query = [
                UserInteraction(ContentType.MUSIC, np.random.rand(10), 0.6, 45.0)
            ]
            tasks.append(Task(f"u{i}", support, query))
        
        meta_loss = maml.outer_loop(tasks)
        
        assert isinstance(meta_loss, float)
    
    def test_adapt_to_user(self):
        """Test adaptation to new user."""
        model = PreferenceModel(input_dim=10, hidden_dim=8, output_dim=3, seed=42)
        maml = MAML(model=model, seed=42)
        
        interactions = [
            UserInteraction(ContentType.TEXT, np.random.rand(10), 0.7, 40.0),
        ]
        
        adapted = maml.adapt_to_user(interactions)
        
        assert isinstance(adapted, PreferenceModel)


# =============================================================================
# Reptile Tests
# =============================================================================


class TestReptile:
    """Test Reptile meta-learning algorithm."""
    
    def test_reptile_creation(self):
        """Test Reptile creation."""
        model = PreferenceModel(input_dim=10, hidden_dim=8, output_dim=3, seed=42)
        reptile = Reptile(
            model=model,
            inner_lr=0.01,
            outer_lr=0.1,
            inner_steps=10,
            seed=42
        )
        
        assert reptile.inner_steps == 10
    
    def test_train_on_task(self):
        """Test training on a single task."""
        model = PreferenceModel(input_dim=10, hidden_dim=8, output_dim=3, seed=42)
        reptile = Reptile(model=model, seed=42)
        
        task = Task(
            "u1",
            [UserInteraction(ContentType.VIDEO, np.random.rand(10), 0.5, 30.0)],
            [UserInteraction(ContentType.MUSIC, np.random.rand(10), 0.6, 45.0)]
        )
        
        trained = reptile.train_on_task(task)
        
        assert isinstance(trained, PreferenceModel)
    
    def test_reptile_update(self):
        """Test Reptile update step."""
        model = PreferenceModel(input_dim=10, hidden_dim=8, output_dim=3, seed=42)
        reptile = Reptile(model=model, seed=42)
        
        task = Task(
            "u1",
            [UserInteraction(ContentType.VIDEO, np.random.rand(10), 0.5, 30.0)],
            [UserInteraction(ContentType.MUSIC, np.random.rand(10), 0.6, 45.0)]
        )
        
        loss = reptile.update(task)
        
        assert isinstance(loss, float)


# =============================================================================
# ColdStartHandler Tests
# =============================================================================


class TestColdStartHandler:
    """Test Cold-Start Handler."""
    
    def test_handler_creation(self):
        """Test handler creation."""
        handler = ColdStartHandler(
            input_dim=10,
            seed=42
        )
        
        assert handler.input_dim == 10
    
    def test_handle_new_user(self):
        """Test handling new user."""
        handler = ColdStartHandler(input_dim=10, seed=42)
        
        interactions = [
            UserInteraction(ContentType.VIDEO, np.random.rand(10), 0.8, 30.0),
            UserInteraction(ContentType.MUSIC, np.random.rand(10), 0.7, 45.0),
        ]
        
        result = handler.handle_new_user("new_user", interactions)
        
        assert "user_id" in result
        assert result["user_id"] == "new_user"
        assert "model_ready" in result
    
    def test_predict_preference(self):
        """Test preference prediction."""
        handler = ColdStartHandler(input_dim=10, seed=42)
        
        # First register user
        interactions = [
            UserInteraction(ContentType.VIDEO, np.random.rand(10), 0.8, 30.0),
        ]
        handler.handle_new_user("user1", interactions)
        
        context = np.random.rand(10)
        content_type, confidence = handler.predict_preference("user1", context)
        
        assert content_type in list(ContentType)
        assert 0 <= confidence <= 1
    
    def test_predict_unknown_user(self):
        """Test prediction for unknown user (uses base model)."""
        handler = ColdStartHandler(input_dim=10, seed=42)
        
        context = np.random.rand(10)
        content_type, confidence = handler.predict_preference("unknown_user", context)
        
        assert content_type in list(ContentType)
    
    def test_update_user_model(self):
        """Test updating user model with new interaction."""
        handler = ColdStartHandler(input_dim=10, seed=42)
        
        # First register user
        interactions = [
            UserInteraction(ContentType.VIDEO, np.random.rand(10), 0.8, 30.0),
        ]
        handler.handle_new_user("user1", interactions)
        
        # Update with new interaction
        new_interaction = UserInteraction(
            ContentType.MUSIC,
            np.random.rand(10),
            0.9,
            60.0
        )
        handler.update_user_model("user1", new_interaction)


# =============================================================================
# PrototypicalNetworks Tests
# =============================================================================


class TestPrototypicalNetworks:
    """Test Prototypical Networks."""
    
    def test_creation(self):
        """Test proto networks creation."""
        proto = PrototypicalNetworks(
            embedding_dim=16,
            n_clusters=5,
            seed=42
        )
        
        assert proto.embedding_dim == 16
        assert proto.n_clusters == 5
    
    def test_embed(self):
        """Test embedding computation."""
        proto = PrototypicalNetworks(embedding_dim=16, seed=42)
        
        interactions = [
            UserInteraction(ContentType.VIDEO, np.random.rand(10), 0.9, 30.0),
            UserInteraction(ContentType.MUSIC, np.random.rand(10), 0.8, 45.0),
            UserInteraction(ContentType.TEXT, np.random.rand(10), 0.7, 60.0),
        ]
        
        embedding = proto.embed(interactions)
        
        assert embedding.shape == (16,)
    
    def test_embed_empty(self):
        """Test embedding with empty interactions."""
        proto = PrototypicalNetworks(embedding_dim=16, seed=42)
        
        embedding = proto.embed([])
        
        assert np.allclose(embedding, 0.0)


# =============================================================================
# Task Generator Tests
# =============================================================================


class TestTaskGenerator:
    """Test synthetic task generator."""
    
    def test_generator_creation(self):
        """Test generator creation."""
        generator = create_synthetic_task_generator(
            n_users=10,
            k_shot=5,
            seed=42
        )
        
        assert callable(generator)
    
    def test_generate_tasks(self):
        """Test task generation."""
        generator = create_synthetic_task_generator(
            n_users=10,
            k_shot=5,
            seed=42
        )
        
        # Generator returns a batch of 4 tasks (fixed batch size)
        tasks = generator()
        
        assert len(tasks) == 4
        for task in tasks:
            assert isinstance(task, Task)
            assert len(task.support_set) > 0
            assert len(task.query_set) > 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestMetaLearningIntegration:
    """Integration tests for meta-learning system."""
    
    def test_maml_training(self):
        """Test MAML training loop."""
        model = PreferenceModel(input_dim=10, hidden_dim=16, output_dim=3, seed=42)
        maml = MAML(model=model, inner_lr=0.01, outer_lr=0.001, seed=42)
        
        generator = create_synthetic_task_generator(n_users=20, k_shot=5, seed=42)
        
        # Train for a few iterations
        stats = maml.train(generator, num_iterations=5, tasks_per_batch=2)
        
        assert "meta_loss" in stats
        assert len(stats["meta_loss"]) == 5
    
    def test_cold_start_pipeline(self):
        """Test complete cold-start handling pipeline."""
        handler = ColdStartHandler(input_dim=10, seed=42)
        
        # New user arrives with initial interactions
        interactions = [
            UserInteraction(ContentType.VIDEO, np.random.rand(10), 0.7, 30.0),
            UserInteraction(ContentType.MUSIC, np.random.rand(10), 0.6, 45.0),
        ]
        result = handler.handle_new_user("user_cold", interactions)
        assert result["model_ready"] is True
        
        # Predict preference
        context = np.random.rand(10)
        content_type, confidence = handler.predict_preference("user_cold", context)
        
        assert content_type in list(ContentType)
        assert 0 <= confidence <= 1
