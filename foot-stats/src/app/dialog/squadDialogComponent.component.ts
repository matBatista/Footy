import { Component, inject, model } from '@angular/core';
import { ActivatedRoute, Router, RouterOutlet } from '@angular/router';
// import { footyService } from '../service/footyService.service';
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

export interface DialogData{
  id_partida: number;
  id_time_a: number;
  id_time_b: number;
  id_jogador_a: number;
  id_jogador_b: number;
  id_campeonato: number;
}

export interface Escalacao {
  pos: string;
  nome: string;
  numero: string;
  atividade: string;
}

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
  
  escalacao_mandante?: Escalacao[] = [];
  escalacao_visitante?: Escalacao[] = [];
  
  private routeSub!: Subscription;
  displayedColumns: string[] = ['pos','nome','numero','atividade'];

  constructor(
    // private footyService: footyService, 
    private route: ActivatedRoute,
    private router: Router) 
  {
    // this.ngInit();
  }

  ngOnInit(): void
  { 
    console.log("this.data:", this.data);
    // this.id_partida = this.data.id_partida;

    this.load();
    // this.routeSub = this.route.params.subscribe(params => {
    //   this.id_campeonato = params['id_campeonato'];
    //   this.id_equipe_a = params['id_equipe_a'];
    //   this.id_equipe_b = params['id_equipe_b'];
    //   this.load();
    // });
  }

  load(){

    console.log("escalacao partida: ", "this.id_partida");
    // this.footyService.obterEscalacaoPartida(this.id_partida).subscribe(
    //   (response) => {
    //     // this.escalacao_visitante = response;
    //     // console.log(response);
    //     this.escalacao_mandante = response.titular.mandante;
    //     this.escalacao_visitante = response.titular.visitante;
    //     console.log("mandante", this.escalacao_mandante);
    //     console.log("visitante", this.escalacao_visitante);
    //   },
    //   (error) => {
    //     console.error('Erro na requisição:', error);
    //   }
    // );

  }

  ngOnDestroy(): void {
    
    if (this.routeSub) {
      this.routeSub.unsubscribe();
    }
  }

  
}
