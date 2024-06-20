export interface Jogador {
    pos: any;
    nome: any;
    numero: any;
    gols: any;
    gols_contra: any;
    cartao: any;
    sub: Jogador | null;
}