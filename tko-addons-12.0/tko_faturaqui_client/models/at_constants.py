# Reference: Portaria n.o 302/2016, de 2 de dezembro
# http://info.portaldasfinancas.gov.pt/pt/informacao_fiscal/legislacao/diplomas_legislativos/Documents/Portaria_302_2016.pdf

at_tax_accounting_bases = {
    'C': 'Contabilidade',
    'E': 'Faturação emitida por terceiros',
    'F': 'Faturação',
    'I': 'Contabilidade integrada com a faturação',
    'P': 'Faturação parcial',
    'R': 'Recibos (a)',
    'S': 'Autofaturação',
    'T': 'Documentos de transporte (a)',
}

at_self_billing_indicators = {
    0: 'Não autofaturação',
    1: 'Autofaturação',
}

at_tax_types = {
    'IVA': 'Imposto sobre o valor acrescentado',
    'IS': 'Imposto do selo',
    'NS': 'Não sujeição a IVA ou IS',
}

at_tax_regions = {
    'PT': 'Portugal continental',  # ADD OTHER COUNTRIES?
    'PT-AC': 'Região Autónoma dos Açores',
    'PT-MA': 'Região Autónoma da Madeira',
}

at_tax_codes = {
    'RED': 'Taxa reduzida',
    'INT': 'Taxa intermédia',
    'NOR': 'Taxa normal',
    'ISE': 'Isenta',
    'OUT': 'Outros',
    'NS': 'Não sujeição',
    'NA': 'Nos recibos emitidos sem imposto discriminado',
}

at_source_billings = {
    'P': 'Documento produzido na aplicação',
    'I': 'Documento integrado e produzido noutra aplicação',
    'M': 'Documento proveniente de recuperação ou de emissão manual',
}

at_invoice_types = {
    'FT': 'Fatura, emitida nos termos do artigo 36.o do Código do IVA',
    'FS': 'Fatura simplificada, emitida nos termos do artigo 40.o do Código do IVA',
    'FR': 'Fatura-recibo',
    'ND': 'Nota de débito',
    'NC': 'Nota de crédito',
}

at_invoice_statuses = {
    'N': 'Normal',
    'S': 'Autofaturação',
    'A': 'Documento anulado',
    'R': 'Documento de resumo doutros documentos criados noutras aplicações e gerado nesta aplicação',
    'F': 'Documento faturado',
}

at_product_types = {
    'P': 'Produtos',
    'S': 'Serviços',
    'O': 'Outros',
    'E': 'Impostos Especiais de Consumo',
    'I': 'Impostos, taxas e encargos parafiscais',
}

at_payment_types = {
    'RC': 'Recibo emitido no âmbito do regime de IVA de Caixa (incluindo os relativos a adiantamentos desse regime)',
    'RG': 'Outros recibos emitidos',
}

at_payment_statuses = {
    'N': 'Recibo normal e vigente',
    'A': 'Recibo anulado',
}

at_source_payments = {
    'P': 'Recibo produzido na aplicação',
    'I': 'Recibo integrado produzido noutra aplicação',
    'M': 'Recibo proveniente de recuperação ou de emissão manual',
}

at_payment_mechanisms = {
    'CC': 'Cartão crédito',
    'CD': 'Cartão débito',
    'CH': 'Cheque bancário',
    'CI': 'Crédito documentário internacional',
    'CO': 'Cheque ou cartão oferta',
    'CS': 'Compensação de saldos em conta corrente',
    'DE': 'Dinheiro eletrónico, por exemplo residente em cartões de fidelidade ou de pontos',
    'LC': 'Letra comercial',
    'MB': 'Referências de pagamento para Multibanco',
    'NU': 'Numerário',
    'OU': 'Outros meios aqui não assinalados',
    'PR': 'Permuta de bens',
    'TB': 'Transferência bancária ou débito direto autorizado',
    'TR': 'Títulos de compensação extrassalarial independentemente do seu suporte, '
          'por exemplo, títulos de refeição, educação, etc.',
}

at_movement_types = {
    'GR': 'Guia de remessa',
    'GT': 'Guia de transporte (incluir aqui as guias globais)',
    'GA': 'Guia de movimentação de ativos fixos próprios',
    'GC': 'Guia de consignação',
    'GD': 'Guia ou nota de devolução',
}

at_movement_statuses = {
    'N': 'Normal',
    'T': 'Por conta de terceiros',
    'A': 'Documento anulado',
    'F': 'Documento faturado, ainda que parcialmente, quando para este documento também existe na tabela 4.1. – '
         'Documentos comerciais a clientes (SalesInvoices) o correspondente do tipo fatura ou fatura simplificada.',
    'R': 'Documento de resumo doutros documentos criados noutras aplicações e gerado nesta aplicação.',
}

# Reference: Manual de Integeração de Software. Comunicação das Faturas á AT

at_tax_exemption_reasons = {
    'M01': 'Artigo 16.º n.º 6 do CIVA (ou similar)',
    'M02': 'Artigo 6.o do Decreto-Lei n.º 198/90, de 19 de Junho',
    'M03': 'Exigibilidade de caixa',
    'M04': 'Isento Artigo 13.º do CIVA (ou similar)',
    'M05': 'Isento Artigo 14.º do CIVA (ou similar)',
    'M06': 'Isento Artigo 15.º do CIVA (ou similar)',
    'M07': 'Isento Artigo 9.º do CIVA (ou similar)',
    'M08': 'IVA - Autoliquidação',
    'M09': 'IVA - Não confere direito a dedução',
    'M10': 'IVA - Regime de isenção',
    'M11': 'Regime particular do tabaco',
    'M12': 'Regime da margem de lucro - Agências de viagens',
    'M13': 'Regime da margem de lucro - Bens em segunda mão',
    'M14': 'Regime da margem de lucro - Objetos de arte',
    'M15': 'Regime da margem de lucro - Objetos de coleção e antiguidades',
    'M16': 'Isento Artigo 14.º do RITI (ou similar)',
    'M20': 'IVA - Regime forfetário',
    'M99': 'Não sujeito; não tributado (ou similar)',
}
