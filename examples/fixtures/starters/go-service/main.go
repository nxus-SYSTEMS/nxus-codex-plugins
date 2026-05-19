package main

import (
	"flag"
	"fmt"
)

func main() {
	provider := flag.String("provider", "offline", "provider name")
	prompt := flag.String("prompt", "hello from Go", "prompt text")
	flag.Parse()

	fmt.Printf("provider=%s prompt=%q\n", *provider, *prompt)
}
