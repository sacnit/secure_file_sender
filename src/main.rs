use std::{error::Error, time::Duration};
use std::net::ToSocketAddrs;
use futures::prelude::*;
use libp2p::{noise, ping, swarm::SwarmEvent, tcp, yamux, Multiaddr};
use tracing_subscriber::EnvFilter;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let _ = tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::from_default_env())
        .try_init();

    let mut swarm = libp2p::SwarmBuilder::with_new_identity()
        .with_tokio()
        .with_tcp(
            tcp::Config::default(),
            noise::Config::new,
            yamux::Config::default,
        )?
        .with_behaviour(|_| ping::Behaviour::default())?
        .build();

        if let Some(input) = std::env::args().nth(1) {
            if let Ok(multiaddr) = input.parse::<Multiaddr>() {
                // If the input is a valid Multiaddr send it
                swarm.dial(multiaddr)?;
                println!("Dialing Multiaddr: {input}");
            } else {
                // Or resolve the input as a domain name or container name
                let port = std::env::args()
                    .nth(2)
                    .unwrap_or_else(|| "12345".to_string()); // Default port if not provided
                let address = format!("{input}:{port}");
    
                if let Ok(mut addrs) = address.to_socket_addrs() {
                    if let Some(socket_addr) = addrs.next() {
                        let resolved_multiaddr: Multiaddr =
                            format!("/ip4/{}/tcp/{}", socket_addr.ip(), socket_addr.port()).parse()?;
                        swarm.dial(resolved_multiaddr.clone())?;
                        println!("Resolved and dialing: {resolved_multiaddr}");
                    } else {
                        eprintln!("Failed to resolve address: {input}");
                    }
                } else {
                    eprintln!("Failed to resolve address: {input}");
                }
            }
        }

    Ok(())
}