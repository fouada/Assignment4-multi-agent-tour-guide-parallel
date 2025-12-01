"""
Tests for Graph Neural Network for Route-Aware Content Selection.

MIT-Level Test Coverage for:
- LocationType enum
- LocationNode dataclass
- RouteEdge dataclass
- RouteGraph class
- GraphConvLayer
- GraphAttentionLayer
- PositionalEncoding
- RouteGNN
- RouteAwareContentSelector

Edge Cases Documented:
- Single node graphs
- Disconnected graphs
- Circular routes
- Empty graphs
"""

import pytest

np = pytest.importorskip("numpy", reason="numpy required for research tests")

from src.research.graph_neural_content import (
    ContentType,
    GraphAttentionLayer,
    GraphConvLayer,
    LocationNode,
    LocationType,
    PositionalEncoding,
    RouteAwareContentSelector,
    RouteEdge,
    RouteGNN,
    RouteGraph,
)

# =============================================================================
# LocationType Tests
# =============================================================================


class TestLocationType:
    """Test LocationType enum."""

    def test_location_types_exist(self):
        """Test all location types exist."""
        assert LocationType.HISTORICAL == "historical"
        assert LocationType.NATURAL == "natural"
        assert LocationType.CULTURAL == "cultural"
        assert LocationType.SCENIC == "scenic"

    def test_location_type_count(self):
        """Test total number of location types."""
        assert len(list(LocationType)) == 9


# =============================================================================
# LocationNode Tests
# =============================================================================


class TestLocationNode:
    """Test LocationNode dataclass."""

    def test_node_creation(self):
        """Test basic node creation."""
        node = LocationNode(
            node_id=0,
            name="Colosseum",
            location_type=LocationType.HISTORICAL,
            coordinates=(41.8902, 12.4922),
            significance=0.95,
            position_in_route=0,
            total_positions=5,
        )
        assert node.node_id == 0
        assert node.name == "Colosseum"
        assert node.location_type == LocationType.HISTORICAL
        assert node.significance == 0.95

    def test_to_feature_vector(self):
        """Test feature vector extraction."""
        node = LocationNode(
            node_id=0,
            name="Museum",
            location_type=LocationType.CULTURAL,
            coordinates=(41.89, 12.49),
            significance=0.9,
            position_in_route=2,
            total_positions=5,
            popularity=0.8,
        )

        features = node.to_feature_vector()

        assert isinstance(features, np.ndarray)
        assert features.dtype == np.float32
        assert not np.any(np.isnan(features))
        assert len(features) == LocationNode.feature_dim()

    def test_feature_dim(self):
        """Test feature dimension."""
        dim = LocationNode.feature_dim()
        assert dim == 16  # 9 (type) + 2 (coords) + 1 (sig) + 2 (pos) + 2 (other)

    # EDGE CASE: First position in route
    def test_first_position(self):
        """Edge case: First position in route."""
        node = LocationNode(
            node_id=0,
            name="Start",
            location_type=LocationType.START,
            coordinates=(0.0, 0.0),
            significance=0.5,
            position_in_route=0,
            total_positions=10,
        )
        features = node.to_feature_vector()
        assert len(features) == LocationNode.feature_dim()

    # EDGE CASE: Single node route
    def test_single_node_route(self):
        """Edge case: Single node in route."""
        node = LocationNode(
            node_id=0,
            name="Only",
            location_type=LocationType.SCENIC,
            coordinates=(45.0, 10.0),
            significance=1.0,
            position_in_route=0,
            total_positions=1,
        )
        features = node.to_feature_vector()
        assert not np.any(np.isnan(features))


# =============================================================================
# RouteEdge Tests
# =============================================================================


class TestRouteEdge:
    """Test RouteEdge dataclass."""

    def test_edge_creation(self):
        """Test basic edge creation."""
        edge = RouteEdge(source=0, target=1, distance_km=5.0, travel_time_min=15.0)
        assert edge.source == 0
        assert edge.target == 1
        assert edge.distance_km == 5.0

    def test_edge_feature_vector(self):
        """Test edge feature vector."""
        edge = RouteEdge(
            source=0,
            target=1,
            distance_km=10.0,
            travel_time_min=20.0,
            edge_type="sequential",
        )

        features = edge.to_feature_vector()

        assert isinstance(features, np.ndarray)
        assert len(features) == 5  # distance + time + 3 edge types


# =============================================================================
# RouteGraph Tests
# =============================================================================


class TestRouteGraph:
    """Test RouteGraph class."""

    def test_empty_graph(self):
        """Test empty graph creation."""
        graph = RouteGraph()
        assert graph.num_nodes == 0
        assert graph.num_edges == 0

    def test_graph_with_nodes(self):
        """Test graph with nodes."""
        nodes = [
            LocationNode(0, "A", LocationType.HISTORICAL, (41.89, 12.49), 0.9, 0, 2),
            LocationNode(1, "B", LocationType.CULTURAL, (41.90, 12.45), 0.8, 1, 2),
        ]
        graph = RouteGraph(nodes=nodes)

        assert graph.num_nodes == 2

    def test_add_sequential_edges(self):
        """Test adding sequential edges."""
        nodes = [
            LocationNode(0, "A", LocationType.HISTORICAL, (41.89, 12.49), 0.9, 0, 3),
            LocationNode(1, "B", LocationType.CULTURAL, (41.90, 12.45), 0.8, 1, 3),
            LocationNode(2, "C", LocationType.SCENIC, (41.91, 12.50), 0.7, 2, 3),
        ]
        graph = RouteGraph(nodes=nodes)
        graph.add_sequential_edges()

        assert graph.num_edges == 2  # A->B, B->C

    def test_get_adjacency_matrix(self):
        """Test adjacency matrix."""
        nodes = [
            LocationNode(0, "A", LocationType.HISTORICAL, (41.89, 12.49), 0.9, 0, 2),
            LocationNode(1, "B", LocationType.CULTURAL, (41.90, 12.45), 0.8, 1, 2),
        ]
        edges = [RouteEdge(0, 1, 5.0, 10.0)]
        graph = RouteGraph(nodes=nodes, edges=edges)

        adj = graph.get_adjacency_matrix()

        assert adj.shape == (2, 2)
        assert adj[0, 1] == 1.0
        assert adj[1, 0] == 1.0  # Undirected

    def test_get_node_features(self):
        """Test node feature matrix."""
        nodes = [
            LocationNode(0, "A", LocationType.HISTORICAL, (41.89, 12.49), 0.9, 0, 2),
            LocationNode(1, "B", LocationType.CULTURAL, (41.90, 12.45), 0.8, 1, 2),
        ]
        graph = RouteGraph(nodes=nodes)

        X = graph.get_node_features()

        assert X.shape == (2, LocationNode.feature_dim())
        assert X.dtype == np.float32

    # EDGE CASE: Single node graph
    def test_single_node_adjacency(self):
        """Edge case: Single node adjacency matrix."""
        nodes = [
            LocationNode(0, "Only", LocationType.SCENIC, (41.89, 12.49), 1.0, 0, 1)
        ]
        graph = RouteGraph(nodes=nodes)

        adj = graph.get_adjacency_matrix()
        assert adj.shape == (1, 1)
        assert adj[0, 0] == 0.0


# =============================================================================
# GraphConvLayer Tests
# =============================================================================


class TestGraphConvLayer:
    """Test Graph Convolutional Layer."""

    def test_layer_creation(self):
        """Test layer creation."""
        layer = GraphConvLayer(in_features=16, out_features=32, seed=42)

        assert layer.in_features == 16
        assert layer.out_features == 32
        assert layer.W.shape == (16, 32)

    def test_forward_pass(self):
        """Test forward pass."""
        layer = GraphConvLayer(in_features=8, out_features=16, seed=42)

        X = np.random.randn(3, 8).astype(np.float32)
        A = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=np.float32)

        output = layer.forward(X, A)

        assert output.shape == (3, 16)
        assert not np.any(np.isnan(output))

    def test_forward_no_bias(self):
        """Test forward without bias."""
        layer = GraphConvLayer(in_features=8, out_features=16, use_bias=False, seed=42)

        X = np.random.randn(3, 8).astype(np.float32)
        A = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]], dtype=np.float32)

        output = layer.forward(X, A)

        assert output.shape == (3, 16)

    # EDGE CASE: Isolated node (no edges)
    def test_isolated_node(self):
        """Edge case: Node with no neighbors."""
        layer = GraphConvLayer(in_features=8, out_features=8, seed=42)

        X = np.random.randn(3, 8).astype(np.float32)
        A = np.array(
            [[0, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=np.float32
        )  # Node 0 isolated

        output = layer.forward(X, A)

        assert not np.any(np.isnan(output))


# =============================================================================
# GraphAttentionLayer Tests
# =============================================================================


class TestGraphAttentionLayer:
    """Test Graph Attention Layer."""

    def test_layer_creation(self):
        """Test layer creation."""
        layer = GraphAttentionLayer(in_features=16, out_features=32, n_heads=4, seed=42)

        assert layer.n_heads == 4

    def test_forward_pass(self):
        """Test forward pass."""
        layer = GraphAttentionLayer(in_features=8, out_features=16, n_heads=2, seed=42)

        X = np.random.randn(4, 8).astype(np.float32)
        A = np.array(
            [[0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0]], dtype=np.float32
        )

        output = layer.forward(X, A)

        assert output.shape == (4, 16)


# =============================================================================
# PositionalEncoding Tests
# =============================================================================


class TestPositionalEncoding:
    """Test Positional Encoding."""

    def test_encoding_creation(self):
        """Test encoding creation."""
        encoding = PositionalEncoding(d_model=16, max_len=100)
        assert encoding.d_model == 16

    def test_encoding_shape(self):
        """Test encoding matrix shape."""
        encoding = PositionalEncoding(d_model=32, max_len=50)
        assert encoding.pe.shape == (50, 32)

    def test_get_encoding(self):
        """Test getting encoding for position."""
        encoding = PositionalEncoding(d_model=16, max_len=100)

        pos_encoding = encoding.pe[5]  # Get encoding for position 5

        assert pos_encoding.shape == (16,)

    def test_encode_method(self):
        """Test encode method with positions list."""
        encoding = PositionalEncoding(d_model=16, max_len=100)

        positions = [0, 1, 2]
        result = encoding.encode(positions)

        assert result.shape == (3, 16)


# =============================================================================
# RouteGNN Tests
# =============================================================================


class TestRouteGNN:
    """Test Route Graph Neural Network."""

    def test_gnn_creation(self):
        """Test GNN creation."""
        gnn = RouteGNN(
            node_features=LocationNode.feature_dim(),
            hidden_dim=32,
            output_dim=3,
            n_layers=2,
            seed=42,
        )

        assert gnn.n_layers == 2

    def test_forward_pass(self):
        """Test forward pass with RouteGraph."""
        gnn = RouteGNN(
            node_features=LocationNode.feature_dim(),
            hidden_dim=16,
            output_dim=3,
            n_layers=2,
            seed=42,
        )

        # Create a RouteGraph
        nodes = [
            LocationNode(0, "A", LocationType.HISTORICAL, (41.89, 12.49), 0.9, 0, 4),
            LocationNode(1, "B", LocationType.CULTURAL, (41.90, 12.45), 0.8, 1, 4),
            LocationNode(2, "C", LocationType.SCENIC, (41.91, 12.50), 0.7, 2, 4),
            LocationNode(3, "D", LocationType.NATURAL, (41.92, 12.55), 0.6, 3, 4),
        ]
        graph = RouteGraph(nodes=nodes)
        graph.add_sequential_edges()

        output = gnn.forward(graph)

        assert output.shape == (4, 3)
        # Should be probabilities (softmax)
        row_sums = output.sum(axis=1)
        assert np.allclose(row_sums, 1.0, atol=1e-5)

    def test_predict(self):
        """Test predict method."""
        gnn = RouteGNN(
            node_features=LocationNode.feature_dim(),
            hidden_dim=16,
            output_dim=3,
            n_layers=2,
            seed=42,
        )

        nodes = [
            LocationNode(0, "A", LocationType.HISTORICAL, (41.89, 12.49), 0.9, 0, 2),
            LocationNode(1, "B", LocationType.CULTURAL, (41.90, 12.45), 0.8, 1, 2),
        ]
        graph = RouteGraph(nodes=nodes)
        graph.add_sequential_edges()

        predictions = gnn.predict(graph)

        assert len(predictions) == 2
        for pred in predictions:
            assert pred in ContentType


# =============================================================================
# RouteAwareContentSelector Tests
# =============================================================================


class TestRouteAwareContentSelector:
    """Test Route-Aware Content Selector."""

    def test_selector_creation(self):
        """Test selector creation."""
        selector = RouteAwareContentSelector(hidden_dim=32, n_layers=2, seed=42)
        assert selector.hidden_dim == 32

    def test_build_graph(self):
        """Test building graph from location dictionaries."""
        selector = RouteAwareContentSelector(seed=42)

        # Note: build_graph expects list of dicts, not LocationNode objects
        locations = [
            {
                "name": "A",
                "type": "historical",
                "lat": 41.89,
                "lon": 12.49,
                "significance": 0.9,
            },
            {
                "name": "B",
                "type": "cultural",
                "lat": 41.90,
                "lon": 12.45,
                "significance": 0.8,
            },
            {
                "name": "C",
                "type": "scenic",
                "lat": 41.91,
                "lon": 12.50,
                "significance": 0.7,
            },
        ]

        graph = selector.build_graph(locations)

        assert graph.num_nodes == 3
        assert graph.num_edges > 0

    def test_select_content(self):
        """Test content selection."""
        selector = RouteAwareContentSelector(seed=42)

        locations = [
            {
                "name": "Start",
                "type": "historical",
                "lat": 41.89,
                "lon": 12.49,
                "significance": 0.9,
            },
            {
                "name": "End",
                "type": "scenic",
                "lat": 41.91,
                "lon": 12.50,
                "significance": 0.8,
            },
        ]

        # select_content returns list of tuples: (name, ContentType, confidence)
        results = selector.select_content(locations)

        assert len(results) == 2
        for name, content_type, confidence in results:
            assert isinstance(name, str)
            assert content_type in ContentType
            assert 0 <= confidence <= 1

    def test_theoretical_analysis(self):
        """Test theoretical analysis."""
        selector = RouteAwareContentSelector(seed=42)
        analysis = selector.get_theoretical_analysis()

        assert "architecture" in analysis
        assert "theoretical_properties" in analysis

    # EDGE CASE: Single location
    def test_single_location(self):
        """Edge case: Single location route."""
        selector = RouteAwareContentSelector(seed=42)

        locations = [
            {
                "name": "Only",
                "type": "scenic",
                "lat": 41.89,
                "lon": 12.49,
                "significance": 1.0,
            }
        ]

        results = selector.select_content(locations)

        assert len(results) == 1


# =============================================================================
# Integration Tests
# =============================================================================


class TestGNNIntegration:
    """Integration tests for GNN content selection."""

    def test_full_pipeline(self):
        """Test complete GNN pipeline."""
        selector = RouteAwareContentSelector(hidden_dim=32, n_layers=2, seed=42)

        # Create route locations as dictionaries
        locations = [
            {
                "name": "Colosseum",
                "type": "historical",
                "lat": 41.8902,
                "lon": 12.4922,
                "significance": 0.95,
            },
            {
                "name": "Roman Forum",
                "type": "historical",
                "lat": 41.8925,
                "lon": 12.4853,
                "significance": 0.9,
            },
            {
                "name": "Trevi Fountain",
                "type": "scenic",
                "lat": 41.9009,
                "lon": 12.4833,
                "significance": 0.85,
            },
            {
                "name": "Pantheon",
                "type": "religious",
                "lat": 41.8986,
                "lon": 12.4769,
                "significance": 0.92,
            },
            {
                "name": "Vatican",
                "type": "religious",
                "lat": 41.9022,
                "lon": 12.4533,
                "significance": 0.98,
            },
        ]

        results = selector.select_content(locations)

        assert len(results) == 5

        # Each selection should have valid content type
        for _name, content_type, confidence in results:
            assert content_type in ContentType
            assert 0 <= confidence <= 1
