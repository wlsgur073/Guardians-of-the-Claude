use clap::Parser;

#[derive(Parser)]
#[command(name = "myapp", about = "A simple CLI tool")]
struct Cli {
    /// Name to greet
    name: String,
}

fn main() {
    let cli = Cli::parse();
    println!("Hello, {}!", cli.name);
}
