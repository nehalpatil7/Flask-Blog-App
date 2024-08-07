// Find all our documentation at https://docs.near.org
import { NearBindgen, near, call, view, initialize, UnorderedMap,Vector } from 'near-sdk-js'


@NearBindgen({})
class InsuranceClaim {
  claims: UnorderedMap<Vector<String>> = new UnorderedMap<Vector<String>>('unique-id-map1');

  @view({}) // This method is read-only and can be called for free
  get_greeting(): Vector<String> {
    if (this.claims.get("insurer_id") != null) {
        return this.claims.get("insurer_id") ;
    } else {
      return new Vector<String>('unique-id-vector2');
    }
  }

  @call({}) // This method changes the state, for which it cost gas
  set_greeting({
    insurer_id,
    claim_info,
  }: {
    insurer_id: string;
    claim_info: string;
  }): void {
   if (this.claims.get(insurer_id) === null) {
      this.claims.set(insurer_id, new Vector<String>('unique-id-vector1'));
    }else{
      const insurerClaims = this.claims.get(insurer_id);
      insurerClaims.push(claim_info);
      this.claims.set(insurer_id, insurerClaims);
    }
  }
}
