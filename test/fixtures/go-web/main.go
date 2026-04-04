package main

import (
	"log"
	"net/http"

	"example.com/myapp/handlers"
)

func main() {
	http.HandleFunc("/hello", handlers.Hello)
	log.Println("Listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
