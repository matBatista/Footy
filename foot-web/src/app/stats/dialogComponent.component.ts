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
import { DialogData } from '../interfaces/DialogData';
import { Fundamentos } from '../interfaces/Fundamentos';
import { Estatisticas } from '../interfaces/Estatisticas';
import e from 'express';

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
  
  fundamento_equipe_a: Fundamentos[] = [];
  fundamento_equipe_b: Fundamentos[] = [];

  estatisticas: Estatisticas[] = [];

  private routeSub!: Subscription;
  displayedColumns: string[] = ['nome','qtdJogos','pros_certos','pros_errados','pros_media','pros_total','cons_certos','cons_errados','cons_media','cons_total'];

  constructor(private footyService: footyService, private route: ActivatedRoute, private router: Router) 
  {
   
  }

  ngOnInit(): void
  { 
   
    
    this.id_campeonato = this.data.id_campeonato;
    this.id_equipe_a = this.data.item.mandante.id;
    this.id_equipe_b = this.data.item.visitante.id;
    console.log(this.data.item);
    
    this.load();

 
  }

  load(){

    this.footyService.obterListaEstatistica(this.id_campeonato,this.id_equipe_a,this.id_equipe_b).subscribe(
      (response) => {
        console.log("estatisticas: ", response);
        this.estatisticas = response;
      },
      (error) => {
        console.error('Erro na requisição:', error);
      }
    );
    // await this.footyService.obterListaEstatistica(this.id_campeonato,this.id_equipe_a,this.id_equipe_b).subscribe(
    //   (response) => {
        
    //     console.log(response);
    //     this.estatisticas = response;
        
    //   },
    //   (error) => {
    //     console.error('Erro na requisição:', error);
    //   }
    // );

    // await this.footyService.obterListaFundamentos(this.id_campeonato,this.id_equipe_b).subscribe(
    //   (response) => {

        
    //     let x = 0;
    //     let f = response;
    //     while(x < f.length){

    //       if( f[x].nome == 'Perda da posse de bola'
    //           || f[x].nome == 'Cartões amarelos' 
    //           || f[x].nome == 'Cartões vermelhos'
    //           || f[x].nome == 'Impedimentos' 
    //           || f[x].nome == 'Rebatidas' 
    //           || f[x].nome == 'Assistências para finalização'
    //         ){
    //           x++
    //       }else{
          
    //         let fundamento: Fundamentos = {
    //           cons_certos: f[x].cons_certos | 0,
    //           cons_errados: f[x].cons_errados | 0,
    //           cons_media: f[x].cons_media | 0,
    //           cons_total: f[x].cons_total | 0,
    //           nome: f[x].nome,
    //           pros_certos: f[x].pros_certos | 0,
    //           pros_errados: f[x].pros_errados | 0,
    //           pros_media: f[x].pros_media | 0,
    //           pros_total: f[x].pros_total | 0,
    //           qtdJogos: f[x].qtdJogos | 0
    //         }

    //         this.fundamento_equipe_b?.push(fundamento);
    //         x++;
    //       }
    //     }
        
    //   },
    //   (error) => {
    //     console.error('Erro na requisição:', error);
    //   }
    // );

    // console.log("this.fundamento_equipe_a", this.fundamento_equipe_a);

    // console.log("estatisticas1", this.estatisticas);
    // let y = 0;

    // while(y < 16){

    //   let nome = this.estatisticas[y].nome;
    //   let equipe_a = this.fundamento_equipe_a.find(x => x.nome === nome) || null;
    //   let equipe_b = this.fundamento_equipe_b.find(x => x.nome === nome) || null;
    //   console.log(nome);
    //   console.log("equipe_a.e",equipe_a);
    //   console.log("equipe_b.e",equipe_b);

    //   this.estatisticas[y].mandante = equipe_a;
    //   this.estatisticas[y].visitante = equipe_b;
    // }
    
    // console.log("estatisticas2", this.estatisticas);

  }

  ngOnDestroy(): void {
    
    if (this.routeSub) {
      this.routeSub.unsubscribe();
    }
  }

  
}
