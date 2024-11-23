package com.example.onetry.certification.dto.res;

import com.example.onetry.certification.entity.Certification;
import lombok.Builder;

import java.time.LocalDate;

@Builder
public record CertificationInfo(
        Long certificationId,
        String certificationName,
        String issuingOrganization,
        LocalDate acquisitionDate,
        String generateFileName

){
    public static CertificationInfo of(Certification certification, String generateFileName){
        return CertificationInfo.builder()
                .certificationId(certification.getId())
                .certificationName(certification.getCertificationName())
                .issuingOrganization(certification.getIssuingOrganization())
                .acquisitionDate(certification.getAcquisitionDate())
                .generateFileName(generateFileName)
                .build();
    }
}
