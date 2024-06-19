import { Component, inject, model } from '@angular/core';
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

export interface DialogData{

  id_time_a: number;
  id_time_b: number;
  id_jogador_a: number;
  id_jogador_b: number;
  id_campeonato: number;
}

export interface Fundamentos {
  nome: string;
  qtdJogos: number;
  pros_certos: number;
  pros_errados: number;
  pros_total: number;
  pros_media: number;
  cons_certos: number;
  cons_errados: number;
  cons_total: number;
  cons_media: number;
  
}

@Component({
  selector: 'dialogComponent',
  templateUrl: './dialogComponent.component.html',
  styleUrl: './dialogComponent.component.scss',
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


export class DialogComponent {
  readonly dialogRef = inject(MatDialogRef<DialogComponent>);
  readonly data = inject<DialogData>(MAT_DIALOG_DATA);
  
  // readonly dados = model(this.data.id_time_a);

  id_campeonato: number | null = null;
  id_equipe_a: number | null = null;
  id_equipe_b: number | null = null;
  clickedRows = new Set<Fundamentos>();
  
  dados_pros?: any[];
  dados_cons?: any[];
  
  fundamento_equipe_a?: Fundamentos[] = [];
  fundamento_equipe_b?: Fundamentos[] = [];
  
  private routeSub!: Subscription;
  displayedColumns: string[] = ['nome','qtdJogos','pros_certos','pros_errados','pros_media','pros_total','cons_certos','cons_errados','cons_media','cons_total'];

  constructor(private footyService: footyService, private route: ActivatedRoute, private router: Router) 
  {
    this.ngInit();
  }

  ngInit(): void
  { 
    console.log(this.data);
    this.id_campeonato = this.data.id_campeonato;
    this.id_equipe_a = this.data.id_time_a;
    this.id_equipe_b = this.data.id_time_b;

    this.load();
    // this.routeSub = this.route.params.subscribe(params => {
      
    //   this.id_campeonato = params['id_campeonato'];
    //   this.id_equipe_a = params['id_equipe_a'];
    //   this.id_equipe_b = params['id_equipe_b'];
    //   this.load();
    // });
  }

  load(){

    // console.log("carrega fundamentos a: ", this.id_equipe_a);
    this.footyService.obterListaFundamentos(this.id_campeonato,this.id_equipe_a,'PROS').subscribe(
      (response) => {
        this.fundamento_equipe_a = response;
        // console.log(this.fundamento_equipe_a);
      },
      (error) => {
        console.error('Erro na requisição:', error);
      }
    );

    // console.log("carrega fundamentos b: ", this.id_equipe_b);
    this.footyService.obterListaFundamentos(this.id_campeonato,this.id_equipe_b, 'PROS').subscribe(
      (response) => {
        // console.log(response);
        this.fundamento_equipe_b = response;
        // console.log(this.fundamento_equipe_b);
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

  
}
