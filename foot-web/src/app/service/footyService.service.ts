import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class footyService {

    url_servico = 'http://localhost:5169';

    constructor(private http: HttpClient) { 

    }

    obterCampeonatos(): Observable<any> {
      const url = this.url_servico + '/campeonato';
      return this.http.get(url);
    }

    obterRodadasCampeonato(id_campeonato: any): Observable<any> {

      const url = this.url_servico + '/campeonato/'+ id_campeonato+'/rodadas';
      return this.http.get(url);
    }

    obterListaFundamentos(id_campeonato: any, id_equipe: any): Observable<any> {
      // int id_campeonato, int id_fundamento, int id_time
      //http://localhost:5169/equipe?id_campeonato=984&id_equipe=1007
      const url = this.url_servico + '/equipe_fundamento?id_campeonato='+ id_campeonato+'&id_equipe='+id_equipe;
      return this.http.get(url);
    }
    obterFundamentoJogador(id_campeonato: any, id_equipe: any): Observable<any> {
      // int id_campeonato, int id_fundamento, int id_time
      //http://localhost:5169/jogador?id_campeonato=984&id_equipe=1007
      const url = this.url_servico + '/jogador/'+ id_campeonato+'/rodadas';
      return this.http.get(url);
    }

    obterEscalacaoPartida(id_partida: any): Observable<any> {
      // int id_campeonato, int id_fundamento, int id_time
      //http://localhost:5169/jogador?id_campeonato=984&id_equipe=1007
      const url = this.url_servico + '/escalacao_partida?id_partida='+id_partida;
      return this.http.get(url);
    }
    
}