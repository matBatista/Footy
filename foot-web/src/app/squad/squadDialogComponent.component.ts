import { Component, inject, model, numberAttribute } from '@angular/core';
import { ActivatedRoute, Router, RouterOutlet } from '@angular/router';
import { footyService } from '../service/footyService.service';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { Subscription } from 'rxjs';
import { DatePipe } from '@angular/common';
import {MatTableModule} from '@angular/material/table';
import {
  MAT_DIALOG_DATA,
  MatDialog,
  MatDialogActions,
  MatDialogClose,
  MatDialogContent,
  MatDialogRef,
  MatDialogTitle,
} from '@angular/material/dialog';
import {MatGridListModule} from '@angular/material/grid-list';
import { DialogData } from '../interfaces/DialogData';
import { Escalacao } from '../interfaces/Escalacao';
import { Jogador } from '../interfaces/Jogador';


@Component({
  selector: 'squadDialogComponent',
  templateUrl: './squadDialogComponent.component.html',
  styleUrl: './squadDialogComponent.component.scss',
  standalone: true,
  imports: [
    CommonModule, 
    RouterOutlet, 
    MatButtonModule, 
    DatePipe, 
    MatTableModule, 
    MatButtonModule,
    MatDialogTitle,
    MatDialogContent,
    MatDialogActions,
    MatDialogClose,
    MatGridListModule
  ],
 
})


export class SquadDialogComponent {
  readonly dialogRef = inject(MatDialogRef<SquadDialogComponent>);
  readonly data = inject<DialogData>(MAT_DIALOG_DATA);
  
  // readonly dados = model(this.data.id_time_a);

  id_partida: number | null = null;
  clickedRows = new Set<Escalacao>();
  
  partida?: any;
  escalacao?: Escalacao[] = [];
  escalacao_mandante?: Escalacao[] = [];
  escalacao_visitante?: Escalacao[] = [];
  
  private routeSub!: Subscription;
  displayedColumns: string[] = ['pos','nome','numero','atividade'];

  constructor(private footyService: footyService, private route: ActivatedRoute, private router: Router) 
  {
    this.ngInit();
  }

  ngInit(): void
  { 
    
    
    this.partida = this.data.item.partida;
    this.id_partida = this.partida.id;
    
    console.log(this.partida);
    
    this.load();
    // this.routeSub = this.route.params.subscribe(params => {
    //   this.id_campeonato = params['id_campeonato'];
    //   this.id_equipe_a = params['id_equipe_a'];
    //   this.id_equipe_b = params['id_equipe_b'];
    //   this.load();
    // });
  }

  load(){

    this.footyService.obterEscalacaoPartida(this.id_partida).subscribe(
      (response) => {
        console.log("escalacao partida: ", response);
        // this.escalacao_visitante = response;
        // console.log(response);

        var m = response.titular.mandante;
        var v = response.titular.visitante;

        let x = 0;
        while(x < 11){


          let j_m: Jogador = {
            pos: m[x].posicao,
            nome: m[x].nomeJogador,
            numero: m[x].numeroDaCamisa.toString().padStart(2, '0'),
            gols: m[x].gols,
            gols_contra: m[x].golsContra,
            cartao: 0,
            sub: m[x].foiSubstituido ? {
              pos: m[x].foiSubstituido.posicao,
              nome: m[x].foiSubstituido.nomeJogador,
              numero: m[x].foiSubstituido.numeroDaCamisa.toString().padStart(2, '0'),
              gols: m[x].foiSubstituido.gols,
              gols_contra: m[x].foiSubstituido.golsContra,
              cartao: 0,
              sub: null
            } : null
          }
          let j_v: Jogador = {
            pos: v[x].posicao,
            nome: v[x].nomeJogador,
            numero: v[x].numeroDaCamisa.toString().padStart(2, '0'),
            gols: v[x].gols,
            gols_contra: v[x].golsContra,
            cartao: 0,
            sub: v[x].foiSubstituido ? {
              pos: v[x].foiSubstituido.posicao,
              nome: v[x].foiSubstituido.nomeJogador,
              numero: v[x].foiSubstituido.numeroDaCamisa.toString().padStart(2, '0'),
              gols: v[x].foiSubstituido.gols,
              gols_contra: v[x].foiSubstituido.golsContra,
              cartao: 0,
              sub: null
            } : null
          }
          let item: Escalacao = {
            mandante: j_m,
            visitante: j_v
          };

          this.escalacao?.push(item);

          x++;
        }
        
        // this.escalacao_mandante = response.titular.mandante;
        // this.escalacao_visitante = response.titular.visitante;
        // console.log("escalacao", this.escalacao);
        // console.log("visitante", this.escalacao_visitante);
      },
      (error) => {
        console.error('Erro na requisição:', error);
      }
    );

  }

  ngOnDestroy(): void {
    
    if (this.routeSub) {
      this.routeSub.unsubscribe();
    }
  }

  createArray(length: number): number[] {

    return new Array(length).fill(0).map((_, i) => i);

  }
  
}
