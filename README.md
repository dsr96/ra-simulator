# A random-access channel simulator for cellular networks

This simulator has been implemented on Python and enables the evaluation of the performance of the random-access channel (RACH) for LTE/5G cellular networks.

The implementation is based on the 3GPP standard reference [1-4].

## Features
- Contention-based random-access channel evaluation for LTE/5G
- Results are exported in csv format to allow post-processing
- By default, metrics are plotted in different figures

## Parameters
The following parameters from the 3GPP standard can be modified:
- PRACH Configuration Index
- Number of available preambles
- Maximum number of attemps for a device before declaring RA failure (preambleTransMax)
- RAR Window Size
- Backoff Indicator

## Metrics
- Blocking probability: probability that a device reaches the maximum number of transmission
  attempts (preambleTransMax) and is unable to complete an access process.
- Average number of preamble retransmissions: average number of preamble retransmissions 
 required to have a success access
- Access delay: time elapsed between the first preamble transmission and the reception of Msg2

## Prerequisites
The following Python libraries are required:
- Pandas
- Numpy
- Matplotlib

## Reference
- [1] NR; NR and NG-RAN Overall description; Stage-2, document TS 38.300, V16.10.0, 3GPP.
- [2] NR; Medium Access Control (MAC) protocol specification, document TS 38.321, V16.10.0, 3GPP.
- [3] NR; Radio Resource Control (RRC); Protocol specification, document TS 38.331, V16.10.0, 3GPP.
- [4] NR; Physical channels and modulation, document TS 38.211, V16.10.0, 3GPP.