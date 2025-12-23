use criterion::{black_box, criterion_group, criterion_main, BenchmarkId, Criterion};
use hyperbolic_curvature::wasserstein::wasserstein1_distance;

fn bench_wasserstein_small(c: &mut Criterion) {
    let mut group = c.benchmark_group("wasserstein_small");

    for size in [2, 5, 10].iter() {
        let n = *size;
        let mu = vec![1.0 / n as f64; n];
        let nu = vec![1.0 / n as f64; n];
        let cost = vec![1.0; n * n];

        group.bench_with_input(BenchmarkId::from_parameter(n), &n, |b, &n| {
            b.iter(|| {
                wasserstein1_distance(
                    black_box(&mu),
                    black_box(&nu),
                    black_box(&cost),
                    black_box(n),
                    black_box(0.01),
                    black_box(100),
                )
            });
        });
    }
    group.finish();
}

fn bench_wasserstein_medium(c: &mut Criterion) {
    let mut group = c.benchmark_group("wasserstein_medium");

    for size in [20, 50, 100].iter() {
        let n = *size;
        let mu = vec![1.0 / n as f64; n];
        let nu = vec![1.0 / n as f64; n];
        let cost = vec![1.0; n * n];

        group.bench_with_input(BenchmarkId::from_parameter(n), &n, |b, &n| {
            b.iter(|| {
                wasserstein1_distance(
                    black_box(&mu),
                    black_box(&nu),
                    black_box(&cost),
                    black_box(n),
                    black_box(0.01),
                    black_box(100),
                )
            });
        });
    }
    group.finish();
}

fn bench_sinkhorn_convergence(c: &mut Criterion) {
    let mut group = c.benchmark_group("sinkhorn_convergence");

    let n = 20;
    let mu = vec![1.0 / n as f64; n];
    let nu = vec![1.0 / n as f64; n];
    let cost = vec![1.0; n * n];

    for max_iter in [10, 50, 100, 500].iter() {
        group.bench_with_input(BenchmarkId::from_parameter(max_iter), max_iter, |b, &max_iter| {
            b.iter(|| {
                wasserstein1_distance(
                    black_box(&mu),
                    black_box(&nu),
                    black_box(&cost),
                    black_box(n),
                    black_box(0.01),
                    black_box(max_iter),
                )
            });
        });
    }
    group.finish();
}

fn bench_different_epsilon(c: &mut Criterion) {
    let mut group = c.benchmark_group("different_epsilon");

    let n = 20;
    let mu = vec![1.0 / n as f64; n];
    let nu = vec![1.0 / n as f64; n];
    let cost = vec![1.0; n * n];

    for epsilon in [0.001, 0.01, 0.1, 1.0].iter() {
        group.bench_with_input(BenchmarkId::from_parameter(epsilon), epsilon, |b, &epsilon| {
            b.iter(|| {
                wasserstein1_distance(
                    black_box(&mu),
                    black_box(&nu),
                    black_box(&cost),
                    black_box(n),
                    black_box(epsilon),
                    black_box(100),
                )
            });
        });
    }
    group.finish();
}

criterion_group!(
    benches,
    bench_wasserstein_small,
    bench_wasserstein_medium,
    bench_sinkhorn_convergence,
    bench_different_epsilon
);
criterion_main!(benches);
