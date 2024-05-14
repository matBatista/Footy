namespace FootAnalises.Model
{
    public class Jogador
    {
        public bool CartaoAmarelo { get; set; }
        public bool CartaoAmarelo2 { get; set; }
        public bool CartaoVermelho { get; set; }
        public bool EmCampo { get; set; }
        public Jogador FoiSubstituido { get; set; }
        public int Gols { get; set; }
        public int GolsContra { get; set; }
        public List<int> GolsInMinutes { get; set; }
        public int Id { get; set; }
        public int IdEquipe { get; set; }
        public int IdJogador { get; set; }
        public int IdPartida { get; set; }
        public int IdPosicao { get; set; }
        public int Indice { get; set; }
        public string Nome { get; set; }
        public string NomeJogador { get; set; }
        public int NumeroDaCamisa { get; set; }
        public string Posicao { get; set; }
        public int Ranking { get; set; }
        public string Tempo { get; set; }
        public bool Titular { get; set; }
    }

}
