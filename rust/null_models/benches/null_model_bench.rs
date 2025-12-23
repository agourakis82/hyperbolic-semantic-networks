use criterion::{black_box, criterion_group, criterion_main, BenchmarkId, Criterion};
use hyperbolic_null_models::configuration::sample_configuration_model;
use hyperbolic_null_models::triadic_rewire::sample_triadic_rewire;
use petgraph::Graph;

fn bench_configuration_model(c: &mut Criterion) {
    let mut group = c.benchmark_group("configuration_model");

    for n_nodes in [10, 20, 50, 100].iter() {
        let n = *n_nodes;
        // Regular degree sequence: all nodes have degree 4
        let degrees = vec![4; n];

        group.bench_with_input(BenchmarkId::from_parameter(n), &n, |b, _| {
            b.iter(|| {
                sample_configuration_model(black_box(&degrees))
            });
        });
    }
    group.finish();
}

fn bench_triadic_rewire(c: &mut Criterion) {
    let mut group = c.benchmark_group("triadic_rewire");

    for n_nodes in [10, 20, 50].iter() {
        let n = *n_nodes;

        // Create test graph (cycle with random edges)
        let mut graph = Graph::new_undirected();
        let nodes: Vec<_> = (0..n).map(|_| graph.add_node(())).collect();

        // Add cycle
        for i in 0..n {
            graph.add_edge(nodes[i], nodes[(i + 1) % n], ());
        }

        // Add some random edges
        for i in (0..n).step_by(3) {
            graph.add_edge(nodes[i], nodes[(i + 2) % n], ());
        }

        group.bench_with_input(BenchmarkId::from_parameter(n), &n, |b, _| {
            b.iter(|| {
                sample_triadic_rewire(black_box(&graph))
            });
        });
    }
    group.finish();
}

fn bench_degree_distribution(c: &mut Criterion) {
    let mut group = c.benchmark_group("degree_distribution");

    for n_nodes in [50, 100, 200].iter() {
        let n = *n_nodes;

        // Power-law-like degree distribution
        let mut degrees = Vec::new();
        for i in 1..=n {
            let degree = (i as f64).powf(-0.5) as usize * 10;
            degrees.push(degree.max(2).min(20));
        }

        // Ensure even sum (required for configuration model)
        let sum: usize = degrees.iter().sum();
        if sum % 2 == 1 {
            degrees[0] += 1;
        }

        group.bench_with_input(BenchmarkId::from_parameter(n), &n, |b, _| {
            b.iter(|| {
                sample_configuration_model(black_box(&degrees))
            });
        });
    }
    group.finish();
}

criterion_group!(
    benches,
    bench_configuration_model,
    bench_triadic_rewire,
    bench_degree_distribution
);
criterion_main!(benches);
