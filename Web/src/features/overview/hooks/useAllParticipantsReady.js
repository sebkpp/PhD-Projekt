export function useAllPlayersReady(players, expectedIds = [1, 2]) {
    return expectedIds.every(id => players[id]?.ready)
}
