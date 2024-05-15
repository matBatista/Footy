namespace Models
{
    public class Partida
    {
        public int IdPartida { get; set; }
        public Reserva Reserva { get; set; }
        public Tecnico TecnicoMandante { get; set; }
        public Tecnico TecnicoVisitante { get; set; }
        public Reserva Titular { get; set; }
    }
}






