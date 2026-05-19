use std::env;

fn main() {
    let prompt = env::args()
        .skip(1)
        .collect::<Vec<_>>()
        .join(" ");

    if prompt.is_empty() {
        println!("pass a prompt to this CLI");
    } else {
        println!("prompt: {prompt}");
    }
}
